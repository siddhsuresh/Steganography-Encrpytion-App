import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import {Index} from "./Index";
import App from "./App";
import "./styles.css";
import { MantineProvider } from "@mantine/core";
import { Router, Route, RootRoute } from "@tanstack/router";
import { Outlet, RouterProvider } from "@tanstack/react-router";
import Decrypt from "./Decrypt";

const rootRoute = new RootRoute({
  component: Root,
});

function Root() {
  return (
    <>
      <Outlet />
    </>
  );
}

const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Index,
});

const appRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/encrypt",
  component: App,
});

const Decrpt = new Route({
  getParentRoute: () => rootRoute,
  path: "/decrypt",
  component: Decrypt,
});

// const howToUseRoute = new Route({
//   getParentRoute: () => rootRoute,
//   path: '/how-to-use',
//   component: HowToUse,
// })
// const contactRoute = new Route({
//   getParentRoute: () => rootRoute,
//   path: '/contact',
//   component: Contact,
// })

// Create the route tree using your routes
const routeTree = rootRoute.addChildren([indexRoute, appRoute,Decrpt]);

// Create the router using your route tree
const router = new Router({ routeTree });

// Register your router for maximum type safety
declare module "@tanstack/router" {
  interface Register {
    router: typeof router;
  }
}

// Render our app!
const rootElement = document.getElementById("root")!;
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <MantineProvider
        theme={{ colorScheme: "light" }}
        withGlobalStyles
        withNormalizeCSS
      >
        <RouterProvider router={router} />
      </MantineProvider>
    </StrictMode>
  );
}
