import { useParams } from "react-router-dom";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { TaskList } from "@/components/dashboard/TaskList";

const listNames: Record<string, string> = {
  "family-chores": "Family Chores",
  "shopping": "Shopping List",
  "projects": "Projects",
  "meetings": "Meetings",
  "personal-todos": "Personal To Dos",
  "habits": "Habits",
};

const ListPage = () => {
  const { listId } = useParams();
  const listName = listId ? listNames[listId] || listId : "List";

  return (
    <DashboardLayout>
      <TaskList />
    </DashboardLayout>
  );
};

export default ListPage;
