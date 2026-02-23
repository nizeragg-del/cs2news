import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const imageUrl = searchParams.get("url");

    if (!imageUrl) {
        return new NextResponse("Missing URL", { status: 400 });
    }

    try {
        const response = await fetch(imageUrl, {
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            },
        });

        if (!response.ok) {
            return new NextResponse("Failed to fetch image", { status: response.status });
        }

        const contentType = response.headers.get("content-type");
        const buffer = await response.arrayBuffer();

        return new NextResponse(buffer, {
            headers: {
                "Content-Type": contentType || "image/jpeg",
                "Cache-Control": "public, max-age=86400", // Cache for 24h
            },
        });
    } catch (error) {
        console.error("Proxy error:", error);
        return new NextResponse("Error proxying image", { status: 500 });
    }
}
