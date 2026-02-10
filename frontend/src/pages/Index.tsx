import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { TaskList } from "@/components/dashboard/TaskList";
import { WeatherAlerts } from "@/components/dashboard/WeatherAlerts";
import { QuickTaskView } from "@/components/dashboard/QuickTaskView";

const Index = () => {
  return (
    <DashboardLayout maxWidth="7xl">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-2">
          <TaskList />
        </div>
        <div className="space-y-6">
          <QuickTaskView />
          <WeatherAlerts />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Index;