"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { MainLayout } from "@/components/layout/main-layout";
import { UploadZone } from "@/components/scanner/upload-zone";
import { ScanResult } from "@/components/scanner/scan-result";
import { uploadDocument } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Shield, Zap } from "lucide-react";

export default function ScannerPage() {
  const [scanResult, setScanResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: (data) => {
      setScanResult(data);
    },
  });

  const handleFileUpload = (file: File) => {
    mutation.mutate(file);
    setScanResult(null); // Reset previous result
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
            Content Compliance Scanner
          </h1>
          <p className="text-gray-600">
            Upload marketing materials, policies, or communications for instant
            compliance review
          </p>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="p-4 bg-blue-50 border-accent/20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <Shield className="text-accent" size={20} />
              </div>
              <div>
                <p className="font-semibold text-sm text-text-dark">
                  AI-Powered Analysis
                </p>
                <p className="text-xs text-gray-600">
                  Checks against RBI regulations
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-green-50 border-success/20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                <Zap className="text-success" size={20} />
              </div>
              <div>
                <p className="font-semibold text-sm text-text-dark">
                  Instant Results
                </p>
                <p className="text-xs text-gray-600">Get feedback in seconds</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Upload Zone */}
        {!scanResult && (
          <UploadZone
            onFileSelect={handleFileUpload}
            isLoading={mutation.isPending}
          />
        )}

        {/* Scan Result */}
        {scanResult && (
          <ScanResult
            result={scanResult}
            onNewScan={() => setScanResult(null)}
          />
        )}
      </div>
    </MainLayout>
  );
}
