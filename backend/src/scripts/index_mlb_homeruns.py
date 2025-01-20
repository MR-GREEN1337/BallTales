# -*- coding: utf-8 -*-
import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import asyncio
from typing import Dict, List
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, func, Index, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("homerun_indexing.log"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()

# SQLAlchemy setup
Base = declarative_base()


class Homerun(Base, AsyncAttrs):
    __tablename__ = "Homerun"

    id = mapped_column(String(length=36), primary_key=True)
    season = mapped_column(Integer, nullable=False)
    title = mapped_column(String, nullable=False)
    exit_velocity = mapped_column(Float, nullable=True)
    launch_angle = mapped_column(Float, nullable=True)
    hit_distance = mapped_column(Float, nullable=True)
    video = mapped_column(String, nullable=True)
    created_at = mapped_column(DateTime, default=func.now())
    updated_at = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_homerun_season", "season"),
        Index("idx_homerun_created_at", "created_at"),
    )


class HomerunIndexer:
    def __init__(self):
        script_dir = Path(__file__).resolve().parent
        self.csv_path = script_dir.parent / "core" / "constants" / "mlb_homeruns.csv"
        self.db_url = os.getenv("DATABASE_URL").replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        self.engine = create_async_engine(
            self.db_url,
            echo=False,
            pool_size=20,  # Increase connection pool size
            max_overflow=30,  # Allow more overflow connections
        )
        self.logger = logging.getLogger(__name__)
        self.batch_size = 500  # Process 500 records at a time

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS homerun CASCADE"))
            self.logger.info("Dropped existing tables")

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            self.logger.info("Created tables and indexes")

    def transform_records(self, df: pd.DataFrame) -> List[Dict]:
        df = df.copy()

        column_mapping = {
            "play_id": "id",
            "ExitVelocity": "exit_velocity",
            "LaunchAngle": "launch_angle",
            "HitDistance": "hit_distance",
        }
        df = df.rename(columns=column_mapping)
        df = df.replace({np.nan: None})

        valid_mask = df["id"].notna() & df["season"].notna() & df["title"].notna()
        df = df[valid_mask]
        df = df.drop_duplicates(subset=["id"], keep="first")

        records = df.to_dict("records")

        for record in records:
            if record.get("title"):
                record["title"] = str(record["title"])
            if record.get("id"):
                record["id"] = str(record["id"])
            if record.get("video"):
                record["video"] = str(record["video"])

        return records

    async def insert_batch(self, records: List[Dict], session: AsyncSession):
        """Insert a batch of records efficiently."""
        stmt = insert(Homerun).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Homerun.id],
            set_={
                "season": stmt.excluded.season,
                "title": stmt.excluded.title,
                "exit_velocity": stmt.excluded.exit_velocity,
                "launch_angle": stmt.excluded.launch_angle,
                "hit_distance": stmt.excluded.hit_distance,
                "video": stmt.excluded.video,
                "updated_at": func.now(),
            },
        )
        await session.execute(stmt)
        await session.commit()

    async def process_batches(self, records: List[Dict]):
        """Process records in parallel batches."""
        async with AsyncSession(self.engine) as session:
            tasks = []
            for i in range(0, len(records), self.batch_size):
                batch = records[i : i + self.batch_size]
                await self.insert_batch(batch, session)
                self.logger.info(
                    f"Processed {min(i + self.batch_size, len(records))}/{len(records)} records"
                )

    async def index_homerun_data(self):
        try:
            await self.drop_tables()
            await self.create_tables()

            df = pd.read_csv(self.csv_path)
            self.logger.info(f"Loaded {len(df)} rows from CSV")

            records = self.transform_records(df)
            self.logger.info(f"Transformed to {len(records)} valid records")

            await self.process_batches(records)

            self.logger.info("Indexing complete!")

        except Exception as e:
            self.logger.error(f"Error indexing homeruns: {str(e)}")
            raise
        finally:
            await self.engine.dispose()


async def main():
    indexer = HomerunIndexer()
    await indexer.index_homerun_data()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Script failed: {str(e)}")
