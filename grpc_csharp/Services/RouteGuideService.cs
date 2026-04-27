using System.Diagnostics;
using Grpc.Core;
using csharp_grpc;

namespace csharp_grpc.Services;

public class RouteGuideService : RouteGuide.RouteGuideBase
{
    private readonly IRouteGuideHelper _routeGuideHelper;
    private readonly ILogger<RouteGuideService> _logger;

    public RouteGuideService(IRouteGuideHelper routeGuideHelper, ILogger<RouteGuideService> logger)
    {
        _routeGuideHelper = routeGuideHelper;
        _logger = logger;
    }

    public override Task<Feature> GetFeature(Point request, ServerCallContext context)
    {
        var feature = _routeGuideHelper.FeatureList.FirstOrDefault(item =>
            item.Location.Latitude == request.Latitude &&
            item.Location.Longitude == request.Longitude);

        return Task.FromResult(feature ?? new Feature { Name = "", Location = request });
    }

    public override async Task ListFeatures(
        Rectangle request,
        IServerStreamWriter<Feature> responseStream,
        ServerCallContext context)
    {
        var left = Math.Min(request.Lo.Longitude, request.Hi.Longitude);
        var right = Math.Max(request.Lo.Longitude, request.Hi.Longitude);
        var bottom = Math.Min(request.Lo.Latitude, request.Hi.Latitude);
        var top = Math.Max(request.Lo.Latitude, request.Hi.Latitude);

        foreach (var feature in _routeGuideHelper.FeatureList)
        {
            var location = feature.Location;
            if (location.Longitude < left || location.Longitude > right || location.Latitude < bottom || location.Latitude > top)
            {
                continue;
            }

            await responseStream.WriteAsync(feature);
        }
    }

    public override async Task<RouteSummary> RecordRoute(IAsyncStreamReader<Point> requestStream, ServerCallContext context)
    {
        var summary = new RouteSummary();
        var stopwatch = Stopwatch.StartNew();
        Point? previous = null;

        await foreach (var point in requestStream.ReadAllAsync())
        {
            summary.PointCount++;
            if (_routeGuideHelper.HasFeature(point))
            {
                summary.FeatureCount++;
            }

            if (previous is not null)
            {
                summary.Distance += GetDistance(previous, point);
            }

            previous = point;
        }

        stopwatch.Stop();
        summary.ElapsedTime = (int)stopwatch.Elapsed.TotalSeconds;
        return summary;
    }

    public override async Task RouteChat(
        IAsyncStreamReader<RouteNote> requestStream,
        IServerStreamWriter<RouteNote> responseStream,
        ServerCallContext context)
    {
        await foreach (var note in requestStream.ReadAllAsync())
        {
            foreach (var previousNote in _routeGuideHelper.GetNotesForLocation(note.Location))
            {
                await responseStream.WriteAsync(previousNote);
            }

            _routeGuideHelper.AddRouteNote(note);
            _logger.LogInformation(
                "Route note received for {Latitude}, {Longitude}",
                note.Location.Latitude,
                note.Location.Longitude);
        }
    }

    private static int GetDistance(Point start, Point end)
    {
        const double coordFactor = 10000000.0;
        const double earthRadiusMeters = 6371000.0;

        var lat1 = DegreesToRadians(start.Latitude / coordFactor);
        var lat2 = DegreesToRadians(end.Latitude / coordFactor);
        var lon1 = DegreesToRadians(start.Longitude / coordFactor);
        var lon2 = DegreesToRadians(end.Longitude / coordFactor);

        var deltaLat = lat2 - lat1;
        var deltaLon = lon2 - lon1;
        var a = Math.Pow(Math.Sin(deltaLat / 2), 2) +
                Math.Cos(lat1) * Math.Cos(lat2) * Math.Pow(Math.Sin(deltaLon / 2), 2);
        var c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));
        return (int)(earthRadiusMeters * c);
    }

    private static double DegreesToRadians(double degrees)
    {
        return degrees * Math.PI / 180.0;
    }
}
