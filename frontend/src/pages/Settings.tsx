import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Settings as SettingsIcon } from "lucide-react";

const Settings = () => {
  return (
    <DashboardLayout>
      <div className="bg-card rounded-lg border border-border p-6">
        <div className="flex items-center gap-3 mb-6">
          <SettingsIcon className="w-6 h-6 text-muted-foreground" />
          <h2 className="text-xl font-semibold">Settings</h2>
        </div>
        <p className="text-muted-foreground">Settings page coming soon...</p>
      </div>
    </DashboardLayout>
  );
};

export default Settings;