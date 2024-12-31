openapi_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Authentication API",
        "description": "API for user authentication and token management.",
        "version": "1.0.0"
    },
    "paths": {
        "/signup": {
            "post": {
                "summary": "User Signup",
                "description": "Sign up a new user and return an API token.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Signup successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "api_token": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Signup failed"}
                }
            }
        },
        "/signin": {
            "post": {
                "summary": "User Signin",
                "description": "Sign in an existing user and return their API token.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Signin successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "api_token": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Signin failed"}
                }
            }
        },
        "/auth_api/email-signup/": {
            "get": {
                "summary": "Email Signup",
                "description": "Sign up with email and return a status message.",
                "parameters": [
                    {"name": "usr", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "pwd", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "email", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Signup successful"},
                    "400": {"description": "Invalid input parameters"},
                    "500": {"description": "Invalid API token"}
                }
            }
        },
        "/auth_api/user-signup/": {
            "get": {
                "summary": "Username Signup",
                "description": "Sign up with username and return a status message.",
                "parameters": [
                    {"name": "usr", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "pwd", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Signup successful"},
                    "400": {"description": "Invalid input parameters"},
                    "500": {"description": "Invalid API token"}
                }
            }
        },
        "/auth_api/email-signin/": {
            "get": {
                "summary": "Email Signin",
                "description": "Sign in with email and return a status message.",
                "parameters": [
                    {"name": "usr", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "pwd", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "email", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Signin successful"},
                    "400": {"description": "Invalid input parameters"},
                    "500": {"description": "Invalid API token"}
                }
            }
        },
        "/auth_api/user-signin/": {
            "get": {
                "summary": "Username Signin",
                "description": "Sign in with username and return a status message.",
                "parameters": [
                    {"name": "usr", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "pwd", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Signin successful"},
                    "400": {"description": "Invalid input parameters"},
                    "500": {"description": "Invalid API token"}
                }
            }
        }
    }
}