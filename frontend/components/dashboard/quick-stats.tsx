import { Card } from "@/components/ui/card";
import { TrendingUp, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { ComplianceScore } from "@/lib/api";

interface Props {
  score?: ComplianceScore;
  loading: boolean;
}

export function QuickStats({ score, loading }: Props) {
  if (loading) {
    return (
      <div className="grid grid-cols-4 gap-4 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-6 h-24 bg-gray-100" />
        ))}
      </div>
    );
  }

  const stats = [
    {
      label: "Compliance Score",
      value: `${score?.score.toFixed(1)}%`,
      icon: TrendingUp,
      color: "text-success",
      bg: "bg-success/10",
    },
    {
      label: "Total Circulars",
      value: score?.total_circulars || 0,
      icon: CheckCircle,
      color: "text-accent",
      bg: "bg-accent/10",
    },
    {
      label: "Critical Issues",
      value: score?.critical_issues || 0,
      icon: AlertTriangle,
      color: "text-critical",
      bg: "bg-critical/10",
    },
    {
      label: "Pending Reviews",
      value: score?.pending_reviews || 0,
      icon: Clock,
      color: "text-warning",
      bg: "bg-warning/10",
    },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.label} className="p-6">
            <div className="flex items-center justify-between mb-3">
              <div
                className={`w-10 h-10 rounded-lg ${stat.bg} flex items-center justify-center`}
              >
                <Icon className={stat.color} size={20} />
              </div>
            </div>
            <p className="text-2xl font-heading font-bold text-text-dark mb-1">
              {stat.value}
            </p>
            <p className="text-sm text-gray-600">{stat.label}</p>
          </Card>
        );
      })}
    </div>
  );
}
