-- AlterTable
ALTER TABLE "User" ADD COLUMN     "avatar" TEXT;

-- AlterTable
ALTER TABLE "UserPreferences" ADD COLUMN     "favoriteHomeRun" TEXT,
ADD COLUMN     "favoritePlayer" TEXT,
ADD COLUMN     "favoriteTeam" TEXT,
ADD COLUMN     "notificationPreference" TEXT NOT NULL DEFAULT 'Game Time Only',
ADD COLUMN     "statsPreference" TEXT NOT NULL DEFAULT 'Basic';

-- CreateTable
CREATE TABLE "BaseballStats" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "messagesExchanged" INTEGER NOT NULL DEFAULT 0,
    "queriesAnswered" INTEGER NOT NULL DEFAULT 0,
    "daysActive" INTEGER NOT NULL DEFAULT 0,
    "lastActive" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "BaseballStats_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "BaseballStats_userId_key" ON "BaseballStats"("userId");

-- AddForeignKey
ALTER TABLE "BaseballStats" ADD CONSTRAINT "BaseballStats_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
