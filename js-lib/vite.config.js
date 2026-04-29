export default {
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      formats: ["es"],
      fileName: "trame-anywidget",
    },
    outDir: "../src/trame_anywidget/esm",
    assetsDir: ".",
  },
};
