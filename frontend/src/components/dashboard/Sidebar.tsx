import {
  Inbox,
  Users,
  Star,
  Calendar,
  CalendarDays,
  FolderOpen,
  List,
  ChevronDown,
  ChevronRight,
  Search,
  Bell,
  MessageCircle,
  Plus,
  Menu,
  X,
  CloudRain,
  Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

interface SmartList {
  icon: React.ElementType;
  label: string;
  path: string;
  count?: number;
}

interface Folder {
  id: string;
  name: string;
  icon: React.ElementType;
  lists: { id: string; name: string; count?: number }[];
}

const smartLists: SmartList[] = [
  { icon: Inbox, label: "Inbox", path: "/", count: 2 },
  { icon: Users, label: "Assigned to me", path: "/assigned", count: 3 },
  { icon: Star, label: "Starred", path: "/starred" },
  { icon: Calendar, label: "Today", path: "/today", count: 4 },
  { icon: CalendarDays, label: "Week", path: "/tasks", count: 7 },
];

const featureLists: SmartList[] = [];

const folders: Folder[] = [
  {
    id: "household",
    name: "Household",
    icon: FolderOpen,
    lists: [
      { id: "family-chores", name: "Family Chores" },
      { id: "shopping", name: "Shopping List", count: 9 },
    ],
  },
  {
    id: "work",
    name: "Work",
    icon: FolderOpen,
    lists: [
      { id: "projects", name: "Projects", count: 5 },
      { id: "meetings", name: "Meetings", count: 2 },
    ],
  },
  {
    id: "personal",
    name: "Personal",
    icon: FolderOpen,
    lists: [
      { id: "personal-todos", name: "Personal To Dos", count: 3 },
      { id: "habits", name: "Habits" },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  const [expandedFolders, setExpandedFolders] = useState<string[]>(["household", "personal"]);
  const location = useLocation();

  // Close sidebar on route change (mobile)
  useEffect(() => {
    if (onClose) {
      onClose();
    }
  }, [location.pathname]);

  const toggleFolder = (folderId: string) => {
    setExpandedFolders(prev => 
      prev.includes(folderId) 
        ? prev.filter(id => id !== folderId)
        : [...prev, folderId]
    );
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      <aside className={cn(
        "fixed left-0 top-10 h-[calc(100vh-2.5rem)] bg-sidebar border-r border-sidebar-border transition-transform duration-300 z-50 flex flex-col w-64",
        // Mobile: hidden by default, shown when isOpen
        "lg:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-sidebar-border">
          <div className="flex items-center gap-2">
            <img src="/favicon.png" alt="Wunderlists" className="w-8 h-8 rounded-lg" />
            <span className="text-sidebar-foreground font-semibold">Wunderlists</span>
          </div>
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-sidebar-muted cursor-pointer hover:text-sidebar-foreground transition-colors" />
            {/* Close button - mobile only */}
            <button 
              onClick={onClose}
              className="p-1 hover:bg-sidebar-accent rounded-md transition-colors lg:hidden"
            >
              <X className="w-5 h-5 text-sidebar-foreground" />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-2 px-2">
          {/* Smart Lists */}
          <div className="space-y-0.5">
            {smartLists.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.label}
                  to={item.path}
                  className={cn(
                    "list-item",
                    isActive && "active bg-sidebar-accent"
                  )}
                >
                  <item.icon className={cn(
                    "w-5 h-5 flex-shrink-0",
                    isActive ? "text-sidebar-foreground" : "text-sidebar-muted"
                  )} />
                  <span className="flex-1 text-sm">{item.label}</span>
                  {item.count && (
                    <span className="text-xs text-sidebar-muted">{item.count}</span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Feature Lists */}
          <div className="mt-4 space-y-0.5 border-t border-sidebar-border pt-2">
            <div className="px-3 py-2 text-xs font-semibold text-sidebar-muted uppercase">
              Features
            </div>
            {featureLists.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.label}
                  to={item.path}
                  className={cn(
                    "list-item",
                    isActive && "active bg-sidebar-accent"
                  )}
                >
                  <item.icon className={cn(
                    "w-5 h-5 flex-shrink-0",
                    isActive ? "text-sidebar-foreground" : "text-sidebar-muted"
                  )} />
                  <span className="flex-1 text-sm">{item.label}</span>
                  {item.count && (
                    <span className="text-xs text-sidebar-muted">{item.count}</span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Folders */}
          <div className="mt-4 space-y-1">
            {folders.map((folder) => {
              const isExpanded = expandedFolders.includes(folder.id);
              return (
                <div key={folder.id}>
                  <button
                    onClick={() => toggleFolder(folder.id)}
                    className="folder-header w-full"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-sidebar-muted" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-sidebar-muted" />
                    )}
                    <folder.icon className="w-4 h-4 text-sidebar-muted" />
                    <span className="flex-1 text-left">{folder.name}</span>
                    <span className="text-xs text-sidebar-muted">•••</span>
                  </button>
                  
                  {isExpanded && (
                    <div className="ml-4 space-y-0.5 animate-fade-in">
                      {folder.lists.map((list) => (
                        <Link
                          key={list.id}
                          to={`/list/${list.id}`}
                          className="list-item pl-6"
                        >
                          <List className="w-4 h-4 text-sidebar-muted" />
                          <span className="flex-1 text-sm">{list.name}</span>
                          {list.count && (
                            <span className="text-xs text-sidebar-muted">{list.count}</span>
                          )}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-sidebar-border">
          <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent rounded-md transition-colors">
            <Plus className="w-4 h-4" />
            Create new list
          </button>
        </div>
      </aside>
    </>
  );
}