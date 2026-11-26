module.exports = {
  // 先把页面跑通，别让 lint 挡住 D1 的静态页验收
  lintOnSave: false,
  devServer: {
    port: 8080,
    // D3 联调时：前端 /api/xxx 会被转发到 C 的 FastAPI
    // 地址写在 .env.local 的 VUE_APP_API_TARGET，改完重启 npm run serve 才生效
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' }
      }
    }
  }
}
