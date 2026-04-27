# Laboratoire gRPC

Structure du dépôt :

- `grpc_python/` : client et serveur Python.
- `grpc_csharp/` : serveur ASP.NET gRPC en C#.
- `protos/route_guide.proto` : contrat partagé.
- `data/route_guide_db.json` : base de données partagée.

Exécution Python :

```powershell
cd grpc_python
py -m grpc_tools.protoc -I ..\protos --python_out=. --grpc_python_out=. ..\protos\route_guide.proto
py server.py
```

Dans un second terminal :

```powershell
cd grpc_python
py client.py
```

Exécution C# :

```powershell
cd grpc_csharp
dotnet run
```

Le client Python utilise `localhost:50051` et peut parler au serveur Python ou au serveur C#.
