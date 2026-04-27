using System.Text.Json;
using csharp_grpc;

namespace csharp_grpc.Services;

public interface IRouteGuideHelper
{
    List<RouteNote> RouteNoteList { get; set; }
    List<Feature> FeatureList { get; set; }
    List<RouteNote> GetNotesForLocation(Point location);
    void AddRouteNote(RouteNote routeNote);
    bool HasFeature(Point point);
}

public class RouteGuideHelper : IRouteGuideHelper
{
    private readonly object _syncRoot = new();

    public List<RouteNote> RouteNoteList { get; set; } = new();
    public List<Feature> FeatureList { get; set; } = new();

    public RouteGuideHelper(IConfiguration configuration, IWebHostEnvironment environment)
    {
        var relativePath = configuration["RouteGuide:FeatureDatabasePath"] ?? "data/route_guide_db.json";
        var dbPath = Path.GetFullPath(Path.Combine(environment.ContentRootPath, relativePath));

        if (!File.Exists(dbPath))
        {
            return;
        }

        var jsonText = File.ReadAllText(dbPath);
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        var dbData = JsonSerializer.Deserialize<List<FeatureRecord>>(jsonText, options) ?? new List<FeatureRecord>();
        FeatureList = dbData
            .Select(item => new Feature
            {
                Name = item.Name ?? string.Empty,
                Location = new Point
                {
                    Latitude = item.Location?.Latitude ?? 0,
                    Longitude = item.Location?.Longitude ?? 0
                }
            })
            .ToList();
    }

    public List<RouteNote> GetNotesForLocation(Point location)
    {
        lock (_syncRoot)
        {
            return RouteNoteList
                .Where(note =>
                    note.Location.Latitude == location.Latitude &&
                    note.Location.Longitude == location.Longitude)
                .Select(note => note.Clone())
                .ToList();
        }
    }

    public void AddRouteNote(RouteNote routeNote)
    {
        lock (_syncRoot)
        {
            RouteNoteList.Add(routeNote.Clone());
        }
    }

    public bool HasFeature(Point point)
    {
        return FeatureList.Any(feature =>
            feature.Location.Latitude == point.Latitude &&
            feature.Location.Longitude == point.Longitude &&
            !string.IsNullOrWhiteSpace(feature.Name));
    }

    private sealed class FeatureRecord
    {
        public string? Name { get; set; }
        public PointRecord? Location { get; set; }
    }

    private sealed class PointRecord
    {
        public int Latitude { get; set; }
        public int Longitude { get; set; }
    }
}
