import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { HabitTracker } from "@/components/dashboard/HabitTracker";

const Habits = () => {
  return (
    <DashboardLayout>
      <HabitTracker />
    </DashboardLayout>
  );
};

export default Habits;