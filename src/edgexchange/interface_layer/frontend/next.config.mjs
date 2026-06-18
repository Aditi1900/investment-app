/** @type {import('next').NextConfig} */
const nextConfig = {
    reactCompiler: true,
    allowedDevOrigins: ['*'],
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "http://localhost:8000/:path*",
            },
        ];
    },
};

export default nextConfig;