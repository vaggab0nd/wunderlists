import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { CalendarDays, RefreshCw, Link2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useCalendarEvents, useSyncGoogleCalendar } from "@/hooks/useRailwayData";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";

const Calendar = () => {
  const { data: events = [], isLoading } = useCalendarEvents();
  const syncCalendar = useSyncGoogleCalendar();
  const { toast } = useToast();

  const handleSync = async () => {
    try {
      await syncCalendar.mutateAsync();
      toast({
        title: "Success",
        description: "Calendar synced successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sync calendar. Make sure you've connected your Google Calendar.",
        variant: "destructive",
      });
    }
  };

  const handleConnect = () => {
    toast({
      title: "Info",
      description: "Google Calendar connection flow would start here. Implement OAuth in the backend.",
    });
  };

  const groupEventsByDate = () => {
    const grouped: Record<string, typeof events> = {};
    events.forEach((event) => {
      const date = format(new Date(event.start_time), "yyyy-MM-dd");
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(event);
    });
    return grouped;
  };

  const groupedEvents = groupEventsByDate();

  return (
    <DashboardLayout>
      <div className="mt-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Calendar</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Synced events from your Google Calendar
            </p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={handleConnect}>
              <Link2 className="w-4 h-4 mr-2" />
              Connect
            </Button>
            <Button onClick={handleSync} disabled={syncCalendar.isPending}>
              <RefreshCw className={`w-4 h-4 mr-2 ${syncCalendar.isPending ? "animate-spin" : ""}`} />
              Sync
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-muted-foreground">
            Loading calendar events...
          </div>
        ) : events.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <CalendarDays className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No calendar events</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Connect your Google Calendar to see your events here.
              </p>
              <Button onClick={handleConnect}>
                <Link2 className="w-4 h-4 mr-2" />
                Connect Google Calendar
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedEvents)
              .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
              .map(([date, dayEvents]) => (
                <div key={date}>
                  <h3 className="text-lg font-semibold mb-3 text-foreground">
                    {format(new Date(date), "EEEE, MMMM d, yyyy")}
                  </h3>
                  <div className="space-y-3">
                    {dayEvents.map((event) => (
                      <Card key={event.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <CardTitle className="text-base">{event.title}</CardTitle>
                              <CardDescription className="mt-1">
                                {format(new Date(event.start_time), "h:mm a")} -{" "}
                                {format(new Date(event.end_time), "h:mm a")}
                              </CardDescription>
                            </div>
                            {event.google_event_id && (
                              <Badge variant="secondary" className="ml-2">
                                <CalendarDays className="w-3 h-3 mr-1" />
                                Google
                              </Badge>
                            )}
                          </div>
                        </CardHeader>
                        {(event.description || event.location) && (
                          <CardContent>
                            {event.location && (
                              <p className="text-sm text-muted-foreground mb-2">
                                📍 {event.location}
                              </p>
                            )}
                            {event.description && (
                              <p className="text-sm text-muted-foreground">
                                {event.description}
                              </p>
                            )}
                          </CardContent>
                        )}
                      </Card>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Calendar;
