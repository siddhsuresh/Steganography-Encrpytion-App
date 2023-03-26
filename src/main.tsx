import React, { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

import {
  Router,
  Route,
  RootRoute,
} from '@tanstack/router'

import {
  Outlet,
  RouterProvider,
} from '@tanstack/react-router'


const rootRoute = new RootRoute({
  component: Root,
})

function Root() {
  return (
    <>
      <div>
      </div>
      <hr />
      <Outlet />
    </>
  )
}

const aboutRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: About,
})

function About() {
  return <div>Hello from About!</div>
}

const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: App,
})

// Create the route tree using your routes
const routeTree = rootRoute.addChildren([indexRoute, aboutRoute])

// Create the router using your route tree
const router = new Router({ routeTree })

// Register your router for maximum type safety
declare module '@tanstack/router' {
  interface Register {
    router: typeof router
  }
}

// Render our app!
const rootElement = document.getElementById('root')!
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}