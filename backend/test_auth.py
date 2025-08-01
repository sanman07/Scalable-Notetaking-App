#!/usr/bin/env python3
"""
Test script for authentication system
Run this to verify the authentication endpoints work correctly
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
}

async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_register():
    """Test user registration"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER
        )
        print(f"Register: {response.status_code}")
        if response.status_code == 201:
            print(f"User created: {response.json()}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 201

async def test_login():
    """Test user login"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Access token: {data['access_token'][:50]}...")
            return data["access_token"]
        else:
            print(f"Error: {response.text}")
            return None

async def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # Test get current user
        response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Get current user: {response.status_code}")
        if response.status_code == 200:
            print(f"Current user: {response.json()}")
        
        # Test create note
        note_data = {
            "title": "Test Note",
            "content": "This is a test note",
            "tags": ["test", "demo"],
            "color": "#6366f1"
        }
        response = await client.post(
            f"{BASE_URL}/notes",
            json=note_data,
            headers=headers
        )
        print(f"Create note: {response.status_code}")
        if response.status_code == 201:
            note = response.json()
            print(f"Note created: {note['title']}")
            
            # Test get notes
            response = await client.get(f"{BASE_URL}/notes", headers=headers)
            print(f"Get notes: {response.status_code}")
            if response.status_code == 200:
                notes = response.json()
                print(f"Found {len(notes)} notes")
            
            # Test create folder
            folder_data = {
                "name": "Test Folder",
                "color": "#ec4899",
                "icon": "📁"
            }
            response = await client.post(
                f"{BASE_URL}/folders",
                json=folder_data,
                headers=headers
            )
            print(f"Create folder: {response.status_code}")
            if response.status_code == 201:
                folder = response.json()
                print(f"Folder created: {folder['name']}")
                
                # Test get folders
                response = await client.get(f"{BASE_URL}/folders", headers=headers)
                print(f"Get folders: {response.status_code}")
                if response.status_code == 200:
                    folders = response.json()
                    print(f"Found {len(folders)} folders")

async def test_invalid_credentials():
    """Test invalid login credentials"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": "nonexistent",
                "password": "wrongpassword"
            }
        )
        print(f"Invalid login: {response.status_code}")
        if response.status_code == 401:
            print("Correctly rejected invalid credentials")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False

async def test_unauthorized_access():
    """Test accessing protected endpoints without authentication"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/notes")
        print(f"Unauthorized access to notes: {response.status_code}")
        if response.status_code == 401:
            print("Correctly rejected unauthorized access")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False

async def main():
    """Run all authentication tests"""
    print("=== Authentication System Test ===")
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Test health check
    print("1. Testing health check...")
    if not await test_health_check():
        print("❌ Health check failed - make sure the server is running")
        return
    print("✅ Health check passed")
    print()
    
    # Test registration
    print("2. Testing user registration...")
    await test_register()
    print()
    
    # Test login
    print("3. Testing user login...")
    token = await test_login()
    if not token:
        print("❌ Login failed")
        return
    print("✅ Login successful")
    print()
    
    # Test protected endpoints
    print("4. Testing protected endpoints...")
    await test_protected_endpoints(token)
    print("✅ Protected endpoints working")
    print()
    
    # Test security
    print("5. Testing security features...")
    await test_invalid_credentials()
    await test_unauthorized_access()
    print("✅ Security features working")
    print()
    
    print("=== Test Complete ===")
    print("If all tests passed, the authentication system is working correctly!")

if __name__ == "__main__":
    asyncio.run(main()) 