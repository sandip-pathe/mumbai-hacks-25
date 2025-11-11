"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings as Bell, Users, Zap } from "lucide-react";

export default function SettingsPage() {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-heading font-extrabold text-text-dark mb-2">
            Settings
          </h1>
          <p className="text-gray-600">
            Configure your compliance monitoring preferences
          </p>
        </div>

        <div className="grid gap-4">
          {/* Notifications */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <Bell className="text-accent" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-text-dark">Notifications</h3>
                <p className="text-sm text-gray-600">
                  Manage alert preferences
                </p>
              </div>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </Card>

          {/* Team Management */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                <Users className="text-success" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-text-dark">
                  Team Management
                </h3>
                <p className="text-sm text-gray-600">
                  Invite users and assign roles
                </p>
              </div>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </Card>

          {/* Integrations */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                <Zap className="text-warning" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-text-dark">Integrations</h3>
                <p className="text-sm text-gray-600">
                  Connect Slack, email, and more
                </p>
              </div>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
