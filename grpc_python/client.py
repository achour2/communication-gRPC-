import grpc

import route_guide_pb2
import route_guide_pb2_grpc


def make_point(latitude, longitude):
    return route_guide_pb2.Point(latitude=latitude, longitude=longitude)


def generate_route():
    points = [
        make_point(407838351, -746143763),
        make_point(408122808, -743999179),
        make_point(409146138, -746188906),
        make_point(411733222, -744228360),
    ]
    for point in points:
        print(f"Envoi du point {point.latitude}, {point.longitude}")
        yield point


def generate_notes():
    notes = [
        route_guide_pb2.RouteNote(
            location=make_point(409146138, -746188906),
            message="Bonjour depuis le client Python",
        ),
        route_guide_pb2.RouteNote(
            location=make_point(409146138, -746188906),
            message="Deuxieme note au meme endroit",
        ),
    ]
    for note in notes:
        print(f"Envoi note: {note.message}")
        yield note


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = route_guide_pb2_grpc.RouteGuideStub(channel)

        print("=== GetFeature ===")
        point = make_point(409146138, -746188906)
        print(stub.GetFeature(point))

        print("=== ListFeatures ===")
        rectangle = route_guide_pb2.Rectangle(
            lo=make_point(400000000, -750000000),
            hi=make_point(420000000, -730000000),
        )
        for feature in stub.ListFeatures(rectangle):
            print(feature)

        print("=== RecordRoute ===")
        summary = stub.RecordRoute(generate_route())
        print(summary)

        print("=== RouteChat ===")
        for note in stub.RouteChat(generate_notes()):
            print(note)


if __name__ == "__main__":
    run()
