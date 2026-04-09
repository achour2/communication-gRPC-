import grpc
import route_guide_pb2
import route_guide_pb2_grpc


def make_point(lat, lon):
    return route_guide_pb2.Point(latitude=lat, longitude=lon)


def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = route_guide_pb2_grpc.RouteGuideStub(channel)

    print("=== GetFeature ===")
    point = make_point(409146138, -746188906)
    feature = stub.GetFeature(point)
    print(feature)

    print("=== ListFeatures ===")
    rectangle = route_guide_pb2.Rectangle(
        lo=make_point(400000000, -750000000),
        hi=make_point(420000000, -730000000)
    )
    for feature in stub.ListFeatures(rectangle):
        print(feature)

    print("=== RecordRoute ===")
    points = [
        make_point(409146138, -746188906),
        make_point(411733222, -744228360),
    ]
    summary = stub.RecordRoute(iter(points))
    print(summary)

    print("=== RouteChat ===")
    notes = [
        route_guide_pb2.RouteNote(
            location=make_point(409146138, -746188906),
            message="Bonjour"
        ),
        route_guide_pb2.RouteNote(
            location=make_point(409146138, -746188906),
            message="Deuxième note"
        ),
    ]

    for response in stub.RouteChat(iter(notes)):
        print(response)


if __name__ == "__main__":
    run()