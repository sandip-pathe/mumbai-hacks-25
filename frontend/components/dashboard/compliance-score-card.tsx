import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp } from "lucide-react";
import { ComplianceScore } from "@/lib/api";

interface Props {
  score?: ComplianceScore;
  loading: boolean;
}

export function ComplianceScoreCard({ score, loading }: Props) {
  if (loading) {
    return (
      <Card className="p-8 animate-pulse">
        <div className="h-40 bg-gray-200 rounded" />
      </Card>
    );
  }

  const scoreValue = score?.score || 0;
  const scoreColor =
    scoreValue >= 80
      ? "text-success"
      : scoreValue >= 60
      ? "text-warning"
      : "text-critical";

  return (
    <Card className="p-8 bg-linear-to-br from-white to-blue-50 border-2 border-accent/20">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">
            Overall Compliance Score
          </p>
          <div className="flex items-baseline gap-3">
            <span
              className={`text-6xl font-heading font-extrabold ${scoreColor}`}
            >
              {scoreValue.toFixed(1)}%
            </span>
            <Badge variant="outline" className="gap-1">
              <TrendingUp size={12} />
              +2.3% from last month
            </Badge>
          </div>
        </div>
      </div>

      {/* Issue Breakdown */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
        <div>
          <p className="text-xs text-gray-500 mb-1">Critical Issues</p>
          <p className="text-2xl font-bold text-critical">
            {score?.critical_issues || 0}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">High Priority</p>
          <p className="text-2xl font-bold text-warning">
            {score?.high_issues || 0}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Pending Reviews</p>
          <p className="text-2xl font-bold text-accent">
            {score?.pending_reviews || 0}
          </p>
        </div>
      </div>

      {/* Category Breakdown */}
      {score?.score_breakdown && (
        <div className="mt-6 space-y-3">
          {Object.entries(score.score_breakdown).map(([category, value]) => (
            <div key={category}>
              <div className="flex justify-between text-sm mb-1">
                <span className="capitalize text-gray-700">
                  {category.replace("_", " ")}
                </span>
                <span className="font-semibold">{value}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-accent transition-all"
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
