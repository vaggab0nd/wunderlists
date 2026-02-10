import { ChevronDown, User, UserPlus, Settings, CalendarDays } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { BackendStatus } from "./BackendStatus";
import { useUsers, useCreateUser } from "@/hooks/useRailwayData";
import { cn } from "@/lib/utils";

export function TopMenuBar() {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const menuRef = useRef<HTMLDivElement>(null);
  
  const { data: users = [] } = useUsers();
  const createUser = useCreateUser();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
        setIsCreatingUser(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleCreateUser = async () => {
    if (!newUserName.trim() || !newUserEmail.trim()) return;
    
    try {
      await createUser.mutateAsync({
        name: newUserName.trim(),
        email: newUserEmail.trim(),
      });
      setNewUserName("");
      setNewUserEmail("");
      setIsCreatingUser(false);
    } catch (error) {
      console.error("Failed to create user:", error);
    }
  };

  return (
    <div className="h-10 bg-card border-b border-border flex items-center justify-between px-4">
      {/* Left side - Quick links like browser bookmarks */}
      <div className="flex items-center gap-4">
        <Link 
          to="/" 
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Dashboard
        </Link>
        <Link 
          to="/tasks" 
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Tasks
        </Link>
        <Link 
          to="/notes" 
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Notes
        </Link>
        <Link 
          to="/habits" 
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Habits
        </Link>
        <Link 
          to="/calendar" 
          className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
        >
          <CalendarDays className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Calendar Sync</span>
        </Link>
      </div>

      {/* Right side - User dropdown and API status */}
      <div className="flex items-center gap-3">
        {/* User dropdown */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md hover:bg-accent transition-colors"
          >
            <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-primary-foreground" />
            </div>
            <span className="text-sm text-foreground hidden sm:inline">Account</span>
            <ChevronDown className={cn(
              "w-4 h-4 text-muted-foreground transition-transform",
              isUserMenuOpen && "rotate-180"
            )} />
          </button>

          {/* Dropdown menu */}
          {isUserMenuOpen && (
            <div className="absolute right-0 top-full mt-1 w-64 bg-popover border border-border rounded-lg shadow-lg z-50 overflow-hidden">
              {/* Current user section */}
              <div className="p-3 border-b border-border">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                    <User className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-popover-foreground">Current User</p>
                    <p className="text-xs text-muted-foreground">user@example.com</p>
                  </div>
                </div>
              </div>

              {/* User list */}
              {users.length > 0 && (
                <div className="py-1 border-b border-border max-h-40 overflow-y-auto">
                  <p className="px-3 py-1 text-xs font-semibold text-muted-foreground uppercase">
                    Switch User
                  </p>
                  {users.map((user) => (
                    <button
                      key={user.id}
                      className="w-full px-3 py-2 flex items-center gap-2 hover:bg-accent text-left transition-colors"
                    >
                      <div className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center">
                        <span className="text-xs text-secondary-foreground">
                          {user.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm text-popover-foreground">{user.name}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Create new user */}
              {isCreatingUser ? (
                <div className="p-3 space-y-2">
                  <input
                    type="text"
                    placeholder="Name"
                    value={newUserName}
                    onChange={(e) => setNewUserName(e.target.value)}
                    className="w-full px-2 py-1.5 text-sm border border-border rounded bg-background text-foreground"
                    autoFocus
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                    className="w-full px-2 py-1.5 text-sm border border-border rounded bg-background text-foreground"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleCreateUser}
                      disabled={createUser.isPending}
                      className="flex-1 px-3 py-1.5 bg-primary text-primary-foreground text-sm rounded hover:opacity-90 disabled:opacity-50 transition-colors"
                    >
                      {createUser.isPending ? "Creating..." : "Create"}
                    </button>
                    <button
                      onClick={() => setIsCreatingUser(false)}
                      className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="py-1">
                  <button
                    onClick={() => setIsCreatingUser(true)}
                    className="w-full px-3 py-2 flex items-center gap-2 hover:bg-accent text-left transition-colors"
                  >
                    <UserPlus className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-popover-foreground">Create New User</span>
                  </button>
                  <Link
                    to="/settings"
                    className="w-full px-3 py-2 flex items-center gap-2 hover:bg-accent text-left transition-colors"
                    onClick={() => setIsUserMenuOpen(false)}
                  >
                    <Settings className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-popover-foreground">Settings</span>
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>

        {/* API Status */}
        <BackendStatus />
      </div>
    </div>
  );
}
