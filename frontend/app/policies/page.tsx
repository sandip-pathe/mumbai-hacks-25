"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { PolicyList } from "@/components/policies/policy-list";

export default function PoliciesPage() {
  const policies = [
    {
      id: "1",
      name: "KYC and Customer Due Diligence",
      version: "v6.4",
      updated: "2025-11-08",
    },
    {
      id: "2",
      name: "Anti-Money Laundering Framework",
      version: "v3.2",
      updated: "2025-10-15",
    },
    {
      id: "3",
      name: "Digital Lending Operations",
      version: "v1.2",
      updated: "2025-09-20",
    },
  ];

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
            Policy Management
          </h1>
          <p className="text-gray-600">
            Version-controlled compliance policies with full audit trail
          </p>
        </div>

        <PolicyList policies={policies} />
      </div>
    </MainLayout>
  );
}
