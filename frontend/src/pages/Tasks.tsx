import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { TaskList } from "@/components/dashboard/TaskList";
import { PrioritizedTasks } from "@/components/dashboard/PrioritizedTasks";
import { OverdueTasks } from "@/components/dashboard/OverdueTasks";
import { TodayTasks } from "@/components/dashboard/TodayTasks";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ListTodo, TrendingUp, AlertCircle, Calendar } from "lucide-react";

const Tasks = () => {
  return (
    <DashboardLayout>
      <div className="bg-card rounded-lg shadow-sm border border-border overflow-hidden">
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="w-full justify-start rounded-none border-b bg-muted/30 p-0 h-auto">
            <TabsTrigger
              value="all"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
            >
              <ListTodo className="w-4 h-4 mr-2" />
              All Tasks
            </TabsTrigger>
            <TabsTrigger
              value="today"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Due Today
            </TabsTrigger>
            <TabsTrigger
              value="overdue"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Overdue
            </TabsTrigger>
            <TabsTrigger
              value="prioritized"
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Prioritized
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="m-0">
            <TaskList />
          </TabsContent>

          <TabsContent value="today" className="m-0">
            <TodayTasks />
          </TabsContent>

          <TabsContent value="overdue" className="m-0">
            <OverdueTasks />
          </TabsContent>

          <TabsContent value="prioritized" className="m-0">
            <PrioritizedTasks />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default Tasks;