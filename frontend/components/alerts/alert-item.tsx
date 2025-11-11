import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/lib/api";
import { AlertCircle, AlertTriangle, Info } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Props {
  alert: Alert;
}

const severityConfig = {
  critical: {
    color: "bg-critical/10 border-critical/30 text-critical",
    icon: AlertCircle,
  },
  high: {
    color: "bg-warning/10 border-warning/30 text-warning",
    icon: AlertTriangle,
  },
  medium: { color: "bg-accent/10 border-accent/30 text-accent", icon: Info },
  low: { color: "bg-gray-100 border-gray-300 text-gray-600", icon: Info },
  info: { color: "bg-blue-100 border-blue-300 text-blue-600", icon: Info },
};

export function AlertItem({ alert }: Props) {
  const config = severityConfig[alert.severity];
  const Icon = config.icon;

  return (
    <Card
      className={`p-4 border-l-4 ${config.color} transition-all hover:shadow-md`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${config.color}`}
        >
          <Icon size={20} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h4 className="font-semibold text-text-dark">{alert.title}</h4>
            <Badge variant="outline" className="shrink-0">
              {alert.alert_type.replace("_", " ")}
            </Badge>
          </div>

          <p className="text-sm text-gray-700 mb-3 leading-relaxed">
            {alert.message}
          </p>

          <p className="text-xs text-gray-500">
            {formatDistanceToNow(new Date(alert.created_at), {
              addSuffix: true,
            })}
          </p>
        </div>
      </div>
    </Card>
  );
}
