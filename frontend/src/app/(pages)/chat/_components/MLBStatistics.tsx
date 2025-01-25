import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  RadarChart,
  Radar,
  RadialBarChart,
  RadialBar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell
} from "recharts";

// Define comprehensive type interfaces based on the schema
interface ChartStyles {
  typography: {
    title: string;
    description: string;
    label: string;
  };
  colors: {
    background: string;
    foreground: string;
    border: string;
    mutedForeground: string;
    chart: Record<string, string>;
    categories?: Record<string, string>;
  };
}

interface ChartComponents {
  legend?: {
    position: 'top' | 'bottom' | 'left' | 'right';
    alignment: 'start' | 'center' | 'end';
  };
  tooltip?: {
    variant: 'default' | 'line' | 'dot' | 'dashed';
    customization?: {
      hideLabel: boolean;
      hideIndicator: boolean;
      indicator: string;
    };
  };
}

interface ChartData {
  chart_type: 'bar' | 'area' | 'pie' | 'radar' | 'radial';
  variant: 'basic' | 'grouped' | 'stacked' | 'expanded' | 'mixed';
  components?: ChartComponents;
  styles: ChartStyles;
  title: string;
  description?: string;
  formatted_data: Array<Record<string, any>>;
  requires_chart: boolean;
}

interface MLBStatisticsProps {
  chart: ChartData;
}

const MLBStatistics: React.FC<MLBStatisticsProps> = ({ chart }) => {
  // Helper function to format dates for display
  const formatDate = (dateString: string) => {
    // First, handle special case where dateString might be already in Month Day format
    if (/^[A-Za-z]+ \d{1,2}$/.test(dateString)) {
      return dateString;
    }

    try {
      // Handle different date formats
      let date: Date;
      
      // Check if the date string is in ISO format (YYYY-MM-DD)
      if (/^\d{4}-\d{2}-\d{2}/.test(dateString)) {
        date = new Date(dateString);
      }
      // Check if it's in MM/DD/YYYY format
      else if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString)) {
        const [month, day, year] = dateString.split('/').map(Number);
        date = new Date(year, month - 1, day);
      }
      // If neither format matches, throw an error
      else {
        throw new Error('Invalid date format');
      }

      // Verify the date is valid
      if (isNaN(date.getTime())) {
        throw new Error('Invalid date');
      }

      return new Intl.DateTimeFormat('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }).format(date);
    } catch (error) {
        console.warn(`Error formatting date: ${dateString}`, error);
        return dateString; // Return original string if formatting fails
      }
    };

  // Generate gradient IDs for area charts
  const getGradientId = (index: number) => `colorGradient-${index}`;

  // Helper to get multiple data keys for grouped/stacked charts
  const getDataKeys = (data: Array<Record<string, any>>): string[] => {
    if (!data.length) return [];
    return Object.keys(data[0]).filter(key => 
      key !== 'date' && key !== 'month' && key !== 'browser' && key !== 'fill'
    );
  };

  const formatMLBTooltip = (value: any, name: string, props: any) => {
    // Check if we're dealing with MLB team data
    const payload = props.payload;
    if (payload && payload[0] && payload[0].payload.label) {
      return [`${value}`, payload[0].payload.label];
    }
    if (payload && payload[0] && payload[0].payload.category) {
      const teamName = payload[0].payload.category;
      return [`${value}`, teamName];
    }
    return [`${value}`, name];
  };

  // Define TypeScript interfaces for our props and data structure
  interface TooltipData {
    label?: string;
    category?: string;
    value: number | string;
    [key: string]: any; // Allow for additional fields
  }
  
  interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{
      payload: TooltipData;
    }>;
    label?: string;
    // Custom styling options
    backgroundColor?: string;
    borderColor?: string;
    labelColor?: string;
    valueColor?: string;
  }
  
  const CustomTooltip: React.FC<CustomTooltipProps> = ({
    active,
    payload,
    label,
    // Default values for styling props
    backgroundColor = "bg-black/90",
    borderColor = "border-white/10",
    labelColor = "text-white",
    valueColor = "text-blue-400"
  }) => {
    // Early return if tooltip shouldn't be shown
    if (!active || !payload || !payload.length) {
      return null;
    }
  
    // Extract data from the payload
    const data = payload[0].payload;
    
    // Format batting average to 3 decimal places
    const formatBattingAverage = (value: number): string => {
      return value.toFixed(3);
    };
  
    return (
      <div className={`${backgroundColor} border ${borderColor} rounded-lg p-3 shadow-lg min-w-[200px]`}>
        {/* Player Name Section */}
        <p className={`text-sm font-medium ${labelColor} mb-2`}>
          {data.label}
        </p>
        
        {/* Batting Average Section */}
        <p className={`text-xs ${valueColor} flex justify-between items-center`}>
          <span>Batting Average:</span>
          <span className={`${labelColor} font-medium`}>
            {formatBattingAverage(data.value as any)}
          </span>
        </p>
      </div>
    );
  };
  
  // Add component display name for better debugging
  CustomTooltip.displayName = 'CustomTooltip';
  

  // Render different chart types
  const renderChart = () => {
    const { chart_type, variant, formatted_data: data } = chart;
    const dataKeys = getDataKeys(data);

    switch (chart_type) {
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data}>
              <defs>
                {dataKeys.map((key, index) => (
                  <linearGradient key={key} id={getGradientId(index)} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={chart.styles.colors.chart[index + 1]} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={chart.styles.colors.chart[index + 1]} stopOpacity={0}/>
                  </linearGradient>
                ))}
              </defs>
              <XAxis 
                dataKey="month" 
                className={chart.styles.typography.label}
              />
              <YAxis className={chart.styles.typography.label} />
              <Tooltip
                contentStyle={{
                  backgroundColor: chart.styles.colors.background,
                  border: `1px solid ${chart.styles.colors.border}`,
                  borderRadius: '8px',
                }}
              />
              {variant === 'stacked' || variant === 'expanded' ? (
                dataKeys.map((key, index) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stackId="1"
                    fill={`url(#${getGradientId(index)})`}
                    stroke={chart.styles.colors.chart[index + 1]}
                  />
                ))
              ) : (
                <Area
                  type="monotone"
                  dataKey={dataKeys[0]}
                  fill={`url(#${getGradientId(0)})`}
                  stroke={chart.styles.colors.chart[1]}
                />
              )}
              {chart.components?.legend && (
                <Legend
                  verticalAlign={chart.components.legend.position as "top" | "bottom"}
                  align={chart.components.legend.alignment as "center" | "right" | "left"}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={data}
                dataKey="visitors"
                nameKey="browser"
                cx="50%"
                cy="50%"
                outerRadius={150}
                label
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`}
                    fill={entry.fill || chart.styles.colors.chart[index + 1]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: chart.styles.colors.background,
                  border: `1px solid ${chart.styles.colors.border}`,
                  borderRadius: '8px',
                }}
              />
              {chart.components?.legend && (
                <Legend
                  verticalAlign={chart.components.legend.position as "top" | "bottom"}
                  align={chart.components.legend.alignment as "center" | "right" | "left"}
                />
              )}
            </PieChart>
          </ResponsiveContainer>
        );

      case 'radar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
              <PolarGrid />
              <PolarAngleAxis dataKey="month" />
              <PolarRadiusAxis />
              {dataKeys.map((key, index) => (
                <Radar
                  key={key}
                  name={key}
                  dataKey={key}
                  stroke={chart.styles.colors.chart[index + 1]}
                  fill={chart.styles.colors.chart[index + 1]}
                  fillOpacity={0.6}
                />
              ))}
              <Tooltip
                contentStyle={{
                  backgroundColor: chart.styles.colors.background,
                  border: `1px solid ${chart.styles.colors.border}`,
                  borderRadius: '8px',
                }}
              />
              {chart.components?.legend && (
                <Legend
                  verticalAlign={chart.components.legend.position as "top" | "bottom"}
                  align={chart.components.legend.alignment as "center" | "right" | "left"}
                />
              )}
            </RadarChart>
          </ResponsiveContainer>
        );

      case 'radial':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <RadialBarChart 
              cx="50%" 
              cy="50%" 
              innerRadius="10%" 
              outerRadius="80%" 
              data={data}
            >
              <RadialBar
                label={{ fill: chart.styles.colors.foreground, position: 'insideStart' }}
                background
                dataKey="visitors"
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`}
                    fill={entry.fill || chart.styles.colors.chart[index + 1]}
                  />
                ))}
              </RadialBar>
              <Tooltip
                contentStyle={{
                  backgroundColor: chart.styles.colors.background,
                  border: `1px solid ${chart.styles.colors.border}`,
                  borderRadius: '8px',
                }}
              />
              {chart.components?.legend && (
                <Legend
                  verticalAlign={chart.components.legend.position as "top" | "bottom"}
                  align={chart.components.legend.alignment as "center" | "right" | "left"}
                  iconSize={10}
                  layout="vertical"
                />
              )}
            </RadialBarChart>
          </ResponsiveContainer>
        );

        case 'bar':
            default:
              return (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={data}>
                    <XAxis 
                      dataKey={data[0]?.category ? 'category' : (data[0]?.month ? 'month' : 'browser')}
                      tickFormatter={data[0]?.date ? formatDate : undefined}
                      className={chart.styles.typography.label}
                      interval={0}
                      angle={-45}
                      textAnchor="end"
                      height={100}
                    />
                    <YAxis 
                      className={chart.styles.typography.label}
                    />
                    {data[0]?.category ? (
                      <Tooltip content={<CustomTooltip />} />
                    ) : (
                      <Tooltip
                        contentStyle={{
                          backgroundColor: chart.styles.colors.background,
                          border: `1px solid ${chart.styles.colors.border}`,
                          borderRadius: '8px',
                        }}
                        formatter={formatMLBTooltip}
                        labelStyle={{ color: chart.styles.colors.foreground }}
                        itemStyle={{ color: chart.styles.colors.mutedForeground }}
                        labelFormatter={data[0]?.date ? formatDate : undefined}
                      />
                    )}
                    {variant === 'grouped' ? (
                      dataKeys.map((key, index) => (
                        <Bar
                          key={key}
                          dataKey={key}
                          fill={chart.styles.colors.chart[index + 1]}
                          radius={[4, 4, 0, 0]}
                        />
                      ))
                    ) : (
                      <Bar
                        dataKey="value"
                        fill={chart.styles.colors.chart[1]}
                        radius={[4, 4, 0, 0]}
                      >
                        {data.map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={chart.styles.colors.chart[(index % 5) + 1]}
                          />
                        ))}
                      </Bar>
                    )}
                    {chart.components?.legend?.position && (
                      <Legend 
                        verticalAlign={chart.components.legend.position as "top" | "bottom"}
                        align={chart.components.legend.alignment as "left" | "center" | "right"} 
                        className={chart.styles.typography.label}
                      />
                    )}
                  </BarChart>
                </ResponsiveContainer>
              );
    }
  };

  // Early return if no chart data is available
  if (!chart) {
    return (
      <Card className="w-full bg-black/50 border-white/10">
        <CardContent>
          <div className="p-4 text-center text-gray-400">
            No chart data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full bg-black/50 border-white/10">
      <CardHeader>
        <CardTitle className={chart.styles.typography.title}>
          {chart.title}
        </CardTitle>
        {chart.description && (
          <p className={chart.styles.typography.description}>
            {chart.description}
          </p>
        )}
      </CardHeader>
      <CardContent>
        {chart.requires_chart ? renderChart() : (
          <div className="p-4 text-center text-gray-400">
            No chart visualization required
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MLBStatistics;