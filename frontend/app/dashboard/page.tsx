"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchComplianceScore, fetchAlerts } from "@/lib/api";
import { MainLayout } from "@/components/layout/main-layout";
import { ComplianceScoreCard } from "@/components/dashboard/compliance-score-card";
import { RecentAlerts } from "@/components/dashboard/recent-alerts";
import { ScoreTrendChart } from "@/components/dashboard/score-trend-chart";
import { QuickStats } from "@/components/dashboard/quick-stats";

export default function DashboardPage() {
  const { data: score, isLoading: scoreLoading } = useQuery({
    queryKey: ["compliance-score"],
    queryFn: fetchComplianceScore,
  });

  const { data: alerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => fetchAlerts(5),
  });

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
            Compliance Overview
          </h1>
          <p className="text-gray-600">
            Real-time monitoring of regulatory compliance status
          </p>
        </div>

        {/* Stats Grid */}
        <QuickStats score={score} loading={scoreLoading} />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - 2/3 width */}
          <div className="lg:col-span-2 space-y-8">
            <ComplianceScoreCard score={score} loading={scoreLoading} />
            <ScoreTrendChart />
          </div>

          {/* Right Column - 1/3 width */}
          <div>
            <RecentAlerts alerts={alerts} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
