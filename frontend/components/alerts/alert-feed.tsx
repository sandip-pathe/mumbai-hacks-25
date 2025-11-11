import { Card } from "@/components/ui/card";
import { AlertItem } from "./alert-item";
import { Alert } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface Props {
  alerts?: Alert[];
  loading: boolean;
}

export function AlertFeed({ alerts, loading }: Props) {
  if (loading) {
    return (
      <Card className="p-12 text-center">
        <Loader2 className="mx-auto animate-spin text-accent mb-4" size={32} />
        <p className="text-gray-600">Loading alerts...</p>
      </Card>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-gray-600">No alerts found</p>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <AlertItem key={alert.id} alert={alert} />
      ))}
    </div>
  );
}
