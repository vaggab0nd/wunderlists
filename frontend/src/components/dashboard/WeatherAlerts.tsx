import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCurrentWeather, useRefreshCurrentWeather } from "@/hooks/useRailwayData";
import { CloudRain, AlertTriangle, RefreshCw, Info, Thermometer } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

export const WeatherAlerts = () => {
  const { data: weatherData = [], isLoading } = useCurrentWeather();
  const refreshWeather = useRefreshCurrentWeather();
  const { toast } = useToast();

  const handleRefresh = async () => {
    try {
      await refreshWeather.mutateAsync();
      toast({
        title: "Success",
        description: "Weather data refreshed",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to refresh weather data",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-muted-foreground">
          Loading weather...
        </CardContent>
      </Card>
    );
  }

  if (weatherData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <CloudRain className="w-5 h-5" />
                Current Weather
              </CardTitle>
              <CardDescription>Dublin & Île de Ré</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRefresh}
              disabled={refreshWeather.isPending}
            >
              <RefreshCw className={`w-4 h-4 ${refreshWeather.isPending ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-4">
            No weather data available
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
              <CloudRain className="w-5 h-5" />
              Current Weather
            </CardTitle>
            <CardDescription>
              Dublin & Île de Ré
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshWeather.isPending}
          >
            <RefreshCw className={`w-4 h-4 ${refreshWeather.isPending ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {weatherData.map((weather) => (
            <div
              key={weather.id}
              className="p-3 rounded-lg border border-border bg-muted/30"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {weather.alert_type === "warning" ? (
                    <AlertTriangle className="w-4 h-4 text-orange-500" />
                  ) : (
                    <CloudRain className="w-4 h-4 text-blue-500" />
                  )}
                  <span className="font-medium text-sm">
                    {weather.location}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Thermometer className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{weather.temperature}°C</span>
                </div>
              </div>
              <div className="ml-6 space-y-1">
                <div className="flex items-center gap-2">
                  <Badge variant={weather.alert_type === "warning" ? "destructive" : "secondary"} className="text-xs">
                    {weather.weather_condition}
                  </Badge>
                </div>
                {weather.message && (
                  <p className="text-xs text-muted-foreground mt-1">{weather.message}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
