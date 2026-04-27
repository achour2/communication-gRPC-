# Laboratoire gRPC

Structure du depot :

- `grpc_python/` : client et serveur Python.
- `grpc_csharp/` : serveur ASP.NET gRPC en C#.
- `protos/route_guide.proto` : contrat partage.
- `data/route_guide_db.json` : base de donnees partagee.

Execution Python :

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

Execution C# :

```powershell
cd grpc_csharp
dotnet run
```

Le client Python utilise `localhost:50051` et peut communiquer avec le serveur Python ou le serveur C#.
