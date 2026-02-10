import { useState } from "react";
import { FileText, Plus, Clock, Loader2, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useNotes, useCreateNote, Note } from "@/hooks/useRailwayData";

// Fallback data
const fallbackNotes: Note[] = [
  { 
    id: "1", 
    title: "Project Ideas", 
    content: "New app concepts for Q2 launch. Focus on productivity tools...", 
    color: "primary",
    updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
  },
  { 
    id: "2", 
    title: "Meeting Notes", 
    content: "Discussed roadmap priorities and resource allocation for next sprint...", 
    color: "accent",
    updated_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
  },
  { 
    id: "3", 
    title: "Book Recommendations", 
    content: "Atomic Habits, Deep Work, The Psychology of Money, Thinking Fast...", 
    color: "info",
    updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  },
];

function formatTimeAgo(dateString?: string): string {
  if (!dateString) return "Just now";
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays === 1) return "Yesterday";
  return `${diffDays} days ago`;
}

export function NotesWidget() {
  const { data: notesFromDb, isLoading, error } = useNotes();
  const createNote = useCreateNote();
  const [activeNote, setActiveNote] = useState<string | null>(null);

  // Use DB data if available, otherwise use fallback
  const notes = (notesFromDb && notesFromDb.length > 0) ? notesFromDb : fallbackNotes;
  const isUsingFallback = !notesFromDb || notesFromDb.length === 0;

  const handleNewNote = () => {
    if (!isUsingFallback) {
      createNote.mutate({ title: "New Note", content: "", color: "primary" });
    }
  };

  const getColorClass = (color?: string) => {
    switch (color) {
      case "primary": return "bg-primary";
      case "accent": return "bg-accent";
      case "info": return "bg-info";
      default: return "bg-primary";
    }
  };

  return (
    <div className="bg-card rounded-lg border border-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div>
          <h3 className="text-lg font-semibold">Notes</h3>
          <p className="text-sm text-muted-foreground">
            {isLoading ? "Loading..." : `${notes.length} notes`}
          </p>
        </div>
        <Button 
          size="sm" 
          onClick={handleNewNote}
          disabled={createNote.isPending}
          className="bg-primary hover:bg-primary/90 text-primary-foreground gap-1.5"
        >
          {createNote.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
          New Note
        </Button>
      </div>

      {/* Notes Grid */}
      <div className="p-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {notes.map((note) => (
          <div
            key={note.id}
            className={cn(
              "p-4 rounded-lg border border-border cursor-pointer transition-all duration-200 hover:shadow-md",
              activeNote === note.id 
                ? "bg-secondary ring-2 ring-primary" 
                : "bg-background hover:bg-secondary/50"
            )}
            onClick={() => setActiveNote(note.id === activeNote ? null : note.id)}
          >
            <div className="flex items-start gap-3">
              <div className={cn(
                "w-1 h-full min-h-[60px] rounded-full flex-shrink-0",
                getColorClass(note.color)
              )} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium truncate">{note.title}</h4>
                  <button className="text-muted-foreground hover:text-foreground">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-3 mb-3">
                  {note.content}
                </p>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  {formatTimeAgo(note.updated_at)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm">
          Using demo data
        </div>
      )}
    </div>
  );
}