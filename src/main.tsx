import React, { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import Index from "./Index";
import Header from "./Header";
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

const links= [
  { "link": "/", "label": "Home" },
  { "link": "/use-app", "label": "Use App" },
  { "link": "/how-to-use", "label": "How to use" },
  { "link": "/contact", "label": "Contact Us" }
]

function Root() {
  return (
    <>
      <Header links={links} />
      <Outlet />
    </>
  )
}

const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Index
})

const appRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/use-app',
  component: App
})
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
const routeTree = rootRoute.addChildren([indexRoute, appRoute])

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