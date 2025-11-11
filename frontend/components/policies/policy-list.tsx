import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, ChevronRight, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Props {
  policy: {
    id: string;
    name: string;
    version: string;
    updated: string;
  };
}

export function PolicyCard({ policy }: Props) {
  return (
    <Card className="p-6 hover:shadow-lg transition-all">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
            <FileText className="text-accent" size={24} />
          </div>

          <div className="flex-1">
            <h3 className="text-lg font-semibold text-text-dark mb-1">
              {policy.name}
            </h3>
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <Badge variant="outline">{policy.version}</Badge>
              <span className="flex items-center gap-1">
                <Clock size={14} />
                Updated{" "}
                {formatDistanceToNow(new Date(policy.updated), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>
        </div>

        <Link href={`/policies/${policy.id}`}>
          <Button variant="ghost" className="gap-2">
            View History
            <ChevronRight size={16} />
          </Button>
        </Link>
      </div>
    </Card>
  );
}

export function PolicyList({
  policies,
}: {
  policies: {
    id: string;
    name: string;
    version: string;
    updated: string;
  }[];
}) {
  return (
    <div className="space-y-4">
      {policies.map((policy) => (
        <PolicyCard key={policy.id} policy={policy} />
      ))}
    </div>
  );
}
