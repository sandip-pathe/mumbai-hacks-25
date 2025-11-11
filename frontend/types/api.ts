export interface ComplianceScore {
  score: number;
  total_circulars: number;
  pending_reviews: number;
  critical_issues: number;
  high_issues: number;
  score_breakdown: {
    [key: string]: number;
  };
  calculated_at: string;
}

export interface Alert {
  id: string;
  alert_type: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  created_at: string;
  circular_id?: string;
}

export interface RBICircular {
  id: string;
  circular_id: string;
  title: string;
  date_published: string;
  status: string;
  url: string;
  pdf_url?: string;
}

export interface PolicyDiff {
  id: string;
  diff_type: string;
  severity: string;
  affected_section: string;
  description: string;
  recommendation: string;
  status: string;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  confidence?: number;
}

export interface Source {
  type: "circular" | "policy";
  title?: string;
  name?: string;
  date?: string;
}
