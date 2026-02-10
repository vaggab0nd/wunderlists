import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import LoadingSpinner from "./components/LoadingSpinner";

// Lazy load all route components for code splitting
const Index = lazy(() => import("./pages/Index"));
const Tasks = lazy(() => import("./pages/Tasks"));
const Notes = lazy(() => import("./pages/Notes"));
const Habits = lazy(() => import("./pages/Habits"));
const Settings = lazy(() => import("./pages/Settings"));
const ListPage = lazy(() => import("./pages/ListPage"));
const Users = lazy(() => import("./pages/Users"));
const Calendar = lazy(() => import("./pages/Calendar"));
const NotFound = lazy(() => import("./pages/NotFound"));

const queryClient = new QueryClient();

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/assigned" element={<Tasks />} />
              <Route path="/starred" element={<Tasks />} />
              <Route path="/today" element={<Tasks />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/list/:listId" element={<ListPage />} />
              <Route path="/notes" element={<Notes />} />
              <Route path="/habits" element={<Habits />} />
              <Route path="/users" element={<Users />} />
              <Route path="/calendar" element={<Calendar />} />
              <Route path="/settings" element={<Settings />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
