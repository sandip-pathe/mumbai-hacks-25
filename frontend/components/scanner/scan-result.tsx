import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, Upload, Clock } from "lucide-react";

interface Props {
  result: any;
  onNewScan: () => void;
}

export function ScanResult({ result, onNewScan }: Props) {
  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card className="p-6 bg-linear-to-br from-white to-blue-50">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
              <CheckCircle className="text-accent" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-heading font-bold text-text-dark mb-1">
                Analysis Complete
              </h3>
              <p className="text-sm text-gray-600">
                File: <span className="font-medium">{result.filename}</span>
              </p>
              <Badge variant="outline" className="mt-2 gap-1">
                <Clock size={12} />
                Pending Approval
              </Badge>
            </div>
          </div>

          <Button onClick={onNewScan} variant="outline" className="gap-2">
            <Upload size={16} />
            New Scan
          </Button>
        </div>
      </Card>

      {/* Circular Info (if detected) */}
      <Card className="p-6">
        <h4 className="font-semibold text-text-dark mb-3 flex items-center gap-2">
          <AlertCircle size={18} />
          Document Processing Status
        </h4>
        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b">
            <span className="text-sm text-gray-600">Circular ID</span>
            <span className="text-sm font-medium">{result.circular_id}</span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-sm text-gray-600">Status</span>
            <Badge variant="secondary">{result.status}</Badge>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-sm text-gray-600">Next Steps</span>
            <span className="text-sm text-gray-600">
              Agent processing in background
            </span>
          </div>
        </div>
      </Card>

      {/* Info Note */}
      <Card className="p-4 bg-blue-50 border-accent/20">
        <p className="text-sm text-gray-700">
          <strong className="text-accent">⚡ Agents Working:</strong> Your
          document is being analyzed by our 5 AI agents. Policy impacts will
          appear in the Alerts tab, and compliance score will update
          automatically.
        </p>
      </Card>
    </div>
  );
}
