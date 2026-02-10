import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTaskSuggestions, useGenerateTaskSuggestions } from "@/hooks/useRailwayData";
import { Sparkles, RefreshCw, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

const priorityColors = {
  high: "destructive",
  medium: "default",
  low: "secondary",
} as const;

export const TaskSuggestions = () => {
  const { data: suggestions = [], isLoading } = useTaskSuggestions();
  const generateSuggestions = useGenerateTaskSuggestions();
  const { toast } = useToast();

  const handleGenerate = async () => {
    try {
      await generateSuggestions.mutateAsync();
      toast({
        title: "Success",
        description: "Task suggestions generated",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate suggestions",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-muted-foreground">
          Loading suggestions...
        </CardContent>
      </Card>
    );
  }

  if (suggestions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Smart Suggestions
              </CardTitle>
              <CardDescription>AI-powered task prioritization</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleGenerate}
              disabled={generateSuggestions.isPending}
            >
              <RefreshCw className={`w-4 h-4 ${generateSuggestions.isPending ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-4">
            Click refresh to generate smart task suggestions
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Smart Suggestions
            </CardTitle>
            <CardDescription>
              {suggestions.length} suggestion{suggestions.length !== 1 ? "s" : ""} to optimize your workflow
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleGenerate}
            disabled={generateSuggestions.isPending}
          >
            <RefreshCw className={`w-4 h-4 ${generateSuggestions.isPending ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {suggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className="p-3 rounded-lg border border-border bg-muted/30"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-medium">Task Priority Suggestion</span>
                </div>
                <Badge variant={priorityColors[suggestion.suggested_priority]}>
                  {suggestion.suggested_priority}
                </Badge>
              </div>
              <div className="ml-6 space-y-1">
                <p className="text-sm">{suggestion.reason}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Confidence:</span>
                  <div className="flex-1 max-w-[100px] h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${suggestion.confidence_score * 100}%` }}
                    />
                  </div>
                  <span>{Math.round(suggestion.confidence_score * 100)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
