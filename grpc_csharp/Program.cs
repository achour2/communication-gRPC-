using csharp_grpc.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddGrpc();
builder.Services.AddSingleton<IRouteGuideHelper, RouteGuideHelper>();

var port = builder.Configuration.GetValue<int?>("RouteGuide:Port") ?? 50051;
builder.WebHost.ConfigureKestrel(serverOptions =>
{
    serverOptions.Listen(System.Net.IPAddress.Loopback, port);
});

var app = builder.Build();

app.MapGrpcService<RouteGuideService>();
app.MapGet("/", () => "Use a gRPC client to communicate with the RouteGuide service.");

app.Run();
