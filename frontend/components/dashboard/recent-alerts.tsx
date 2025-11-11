import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/lib/api";
import { AlertItem } from "@/components/alerts/alert-item";
import { ArrowRight } from "lucide-react";

interface Props {
  alerts?: Alert[];
}

export function RecentAlerts({ alerts }: Props) {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-heading font-bold text-text-dark">
          Recent Alerts
        </h3>
        <Link href="/alerts">
          <Button variant="ghost" size="sm" className="gap-1">
            View All
            <ArrowRight size={14} />
          </Button>
        </Link>
      </div>

      <div className="space-y-3">
        {alerts?.slice(0, 5).map((alert) => (
          <AlertItem key={alert.id} alert={alert} />
        ))}

        {(!alerts || alerts.length === 0) && (
          <p className="text-sm text-gray-500 text-center py-8">
            No recent alerts
          </p>
        )}
      </div>
    </Card>
  );
}
