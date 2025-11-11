import { Card } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Mock data - replace with real data from API
const mockData = [
  { date: "Oct 1", score: 78 },
  { date: "Oct 8", score: 80 },
  { date: "Oct 15", score: 82 },
  { date: "Oct 22", score: 79 },
  { date: "Oct 29", score: 83 },
  { date: "Nov 5", score: 85 },
  { date: "Nov 12", score: 87 },
];

export function ScoreTrendChart() {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-heading font-bold text-text-dark mb-4">
        Compliance Score Trend
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={mockData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="date" stroke="#6B7280" />
          <YAxis domain={[0, 100]} stroke="#6B7280" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFF",
              border: "1px solid #E5E7EB",
              borderRadius: "8px",
            }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3D6DEB"
            strokeWidth={3}
            dot={{ fill: "#3D6DEB", r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
