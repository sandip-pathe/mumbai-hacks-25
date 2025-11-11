"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { MainLayout } from "@/components/layout/main-layout";
import { AlertFeed } from "@/components/alerts/alert-feed";
import { fetchAlerts } from "@/lib/api";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AlertsPage() {
  const [severity, setSeverity] = useState<string | undefined>();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ["alerts", severity],
    queryFn: () => fetchAlerts(50, severity),
    refetchInterval: 10000, // Poll every 10 seconds
  });

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
              Compliance Alerts
            </h1>
            <p className="text-gray-600">
              Real-time notifications from regulatory monitoring agents
            </p>
          </div>

          {/* Filters */}
          <Tabs
            value={severity || "all"}
            onValueChange={(v) => setSeverity(v === "all" ? undefined : v)}
          >
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="critical">Critical</TabsTrigger>
              <TabsTrigger value="high">High</TabsTrigger>
              <TabsTrigger value="medium">Medium</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Alert Feed */}
        <AlertFeed alerts={alerts} loading={isLoading} />
      </div>
    </MainLayout>
  );
}
