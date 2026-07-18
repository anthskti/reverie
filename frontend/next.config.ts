import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000" },
      { protocol: "https", hostname: "**" },
    ],
  },
  async redirects() {
    return [
      {
        source: "/projects",
        destination: "/profile",
        permanent: false, // Use false while refactoring to not cache aggressive redirects
      },
      {
        source: "/inventory",
        destination: "/profile",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
