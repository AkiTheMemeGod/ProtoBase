openapi_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Flask API Documentation",
        "version": "1.0.0",
        "description": "API documentation for the Flask application."
    },
    "paths": {
        "/delete_project": {
            "post": {
                "summary": "Delete a project",
                "description": "Deletes a project for the currently logged-in user.",
                "parameters": [
                    {
                        "name": "project_name",
                        "in": "formData",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "302": {
                        "description": "Redirects to the dashboard after deletion."
                    }
                }
            }
        },
        "/logout": {
            "get": {
                "summary": "Logout user",
                "description": "Logs out the currently logged-in user and redirects to the get-started page.",
                "responses": {
                    "302": {
                        "description": "Redirects to the get-started page."
                    }
                }
            }
        },

        "/get-started": {
            "get": {
                "summary": "Get Started",
                "description": "Renders the get-started page or redirects to the dashboard if logged in.",
                "responses": {
                    "200": {
                        "description": "Get-started page rendered."
                    },
                    "302": {
                        "description": "Redirects to the dashboard."
                    }
                }
            }
        },
        "/signup": {
            "post": {
                "summary": "Sign up",
                "description": "Allows a new user to sign up.",
                "parameters": [
                    {"name": "username", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "password", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {
                                        "type": "string"
                                    },
                                    "password": {
                                        "type": "string"
                                    }
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Signup success."
                    },
                    "400": {
                        "description": "Signup failed."
                    }
                }
            }
        },
        "/signin": {
            "post": {
                "summary": "Sign in",
                "description": "Authenticates a user.",
                "parameters": [
                    {"name": "username", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "password", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {
                                        "type": "string"
                                    },
                                    "password": {
                                        "type": "string"
                                    }
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Signin success."
                    },
                    "400": {
                        "description": "Signin failed."
                    }
                }
            }
        },
        "/add_project": {
            "post": {
                "summary": "Add a project",
                "description": "Adds a new project for the logged-in user.",
                "parameters": [
                    {
                        "name": "project_name",
                        "in": "formData",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "302": {
                        "description": "Redirects to the dashboard."
                    }
                }
            }
        },

        "/auth_api/email-signup/": {
            "get": {
                "summary": "Email Signup",
                "description": "Signup using email, username, and password.",
                "parameters": [
                    {
                        "name": "usr",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "pwd",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "email",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "token",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Signup success."
                    },
                    "400": {
                        "description": "Invalid input parameters."
                    },
                    "500": {
                        "description": "Invalid API token."
                    }
                }
            }
        },
        "/auth_api/user-signup/": {
            "get": {
                "summary": "Username Signup",
                "description": "Signup using username and password.",
                "parameters": [
                    {
                        "name": "usr",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "pwd",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "token",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Signup success."
                    },
                    "400": {
                        "description": "Invalid input parameters."
                    },
                    "500": {
                        "description": "Invalid API token."
                    }
                }
            }
        },
        "/auth_api/email-signin/": {
            "get": {
                "summary": "Email Signin",
                "description": "Signin using email, username, and password.",
                "parameters": [
                    {
                        "name": "usr",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "pwd",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "email",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "token",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Signin success."
                    },
                    "400": {
                        "description": "Invalid input parameters or incorrect credentials."
                    },
                    "500": {
                        "description": "Invalid API token."
                    }
                }
            }
        },
        "/auth_api/user-signin/": {
            "get": {
                "summary": "Username Signin",
                "description": "Signin using username and password.",
                "parameters": [
                    {
                        "name": "usr",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "pwd",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "token",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Signin success."
                    },
                    "400": {
                        "description": "Invalid input parameters or incorrect credentials."
                    },
                    "500": {
                        "description": "Invalid API token."
                    }
                }
            }
        }
    }
}
