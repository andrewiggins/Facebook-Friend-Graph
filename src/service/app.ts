import * as express from "express";
import * as path from "path";

export const app: express.Express = express();

app.set("views", path.join(__dirname, "./views/"));
app.set("view engine", "hbs");

app.use("/dist", express.static(path.join(__dirname, "..", "..", "dist")));

app.get("/", (req, res) => {
    res.render("index");
});
