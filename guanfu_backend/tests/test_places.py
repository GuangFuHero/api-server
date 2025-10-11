"""
Comprehensive test suite for Places API following TDD principles.

Test Coverage:
- Create place (success, validation errors)
- Get place by ID (success, not found)
- List places (pagination, filtering by status/type)
- Update place (success, not found, API key protection)
"""
import pytest
from fastapi import status


class TestCreatePlace:
    """Test suite for POST /places endpoint."""

    def test_create_place_with_full_data_success(self, client, sample_place_data):
        """Test creating a place with all fields provided."""
        response = client.post("/places", json=sample_place_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify all fields are returned
        assert data["name"] == sample_place_data["name"]
        assert data["address"] == sample_place_data["address"]
        assert data["address_description"] == sample_place_data["address_description"]
        assert data["coordinates"] == sample_place_data["coordinates"]
        assert data["type"] == sample_place_data["type"]
        assert data["sub_type"] == sample_place_data["sub_type"]
        assert data["info_sources"] == sample_place_data["info_sources"]
        assert data["verified_at"] == sample_place_data["verified_at"]
        assert data["website_url"] == sample_place_data["website_url"]
        assert data["status"] == sample_place_data["status"]
        assert data["resources"] == sample_place_data["resources"]
        assert data["open_date"] == sample_place_data["open_date"]
        assert data["end_date"] == sample_place_data["end_date"]
        assert data["open_time"] == sample_place_data["open_time"]
        assert data["end_time"] == sample_place_data["end_time"]
        assert data["contact_name"] == sample_place_data["contact_name"]
        assert data["contact_phone"] == sample_place_data["contact_phone"]
        assert data["notes"] == sample_place_data["notes"]
        assert data["tags"] == sample_place_data["tags"]
        assert data["additional_info"] == sample_place_data["additional_info"]

        # Verify auto-generated fields
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_create_place_with_minimal_data_success(self, client, sample_place_minimal_data):
        """Test creating a place with only required fields."""
        response = client.post("/places", json=sample_place_minimal_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify required fields
        assert data["name"] == sample_place_minimal_data["name"]
        assert data["address"] == sample_place_minimal_data["address"]
        assert data["coordinates"] == sample_place_minimal_data["coordinates"]
        assert data["type"] == sample_place_minimal_data["type"]
        assert data["status"] == sample_place_minimal_data["status"]
        assert data["contact_name"] == sample_place_minimal_data["contact_name"]
        assert data["contact_phone"] == sample_place_minimal_data["contact_phone"]

        # Verify optional fields are null/empty
        assert data.get("address_description") is None
        assert data.get("sub_type") is None
        assert data.get("website_url") is None

    def test_create_place_missing_required_name(self, client, sample_place_minimal_data):
        """Test creating place without required 'name' field."""
        data = sample_place_minimal_data.copy()
        del data["name"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_address(self, client, sample_place_minimal_data):
        """Test creating place without required 'address' field."""
        data = sample_place_minimal_data.copy()
        del data["address"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_coordinates(self, client, sample_place_minimal_data):
        """Test creating place without required 'coordinates' field."""
        data = sample_place_minimal_data.copy()
        del data["coordinates"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_type(self, client, sample_place_minimal_data):
        """Test creating place without required 'type' field."""
        data = sample_place_minimal_data.copy()
        del data["type"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_status(self, client, sample_place_minimal_data):
        """Test creating place without required 'status' field."""
        data = sample_place_minimal_data.copy()
        del data["status"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_contact_name(self, client, sample_place_minimal_data):
        """Test creating place without required 'contact_name' field."""
        data = sample_place_minimal_data.copy()
        del data["contact_name"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_missing_required_contact_phone(self, client, sample_place_minimal_data):
        """Test creating place without required 'contact_phone' field."""
        data = sample_place_minimal_data.copy()
        del data["contact_phone"]

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetPlace:
    """Test suite for GET /places/{id} endpoint."""

    def test_get_place_by_id_success(self, client, sample_place_data):
        """Test retrieving a place by ID successfully."""
        # First create a place
        create_response = client.post("/places", json=sample_place_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        place_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/places/{place_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == place_id
        assert data["name"] == sample_place_data["name"]
        assert data["address"] == sample_place_data["address"]
        assert data["coordinates"] == sample_place_data["coordinates"]

    def test_get_place_by_id_not_found(self, client):
        """Test retrieving a non-existent place returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/places/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_place_with_all_jsonb_fields(self, client, sample_place_data):
        """Test that JSONB fields (coordinates, resources, tags, additional_info) are correctly returned."""
        # Create place
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Get place
        response = client.get(f"/places/{place_id}")
        data = response.json()

        # Verify JSONB fields are correctly deserialized
        assert data["coordinates"] == sample_place_data["coordinates"]
        assert data["resources"] == sample_place_data["resources"]
        assert data["tags"] == sample_place_data["tags"]
        assert data["additional_info"] == sample_place_data["additional_info"]


class TestListPlaces:
    """Test suite for GET /places endpoint (list with pagination and filters)."""

    def test_list_places_default_pagination(self, client, sample_place_data):
        """Test listing places with default pagination."""
        # Create multiple places
        for i in range(3):
            data = sample_place_data.copy()
            data["name"] = f"Place {i}"
            client.post("/places", json=data)

        # List places
        response = client.get("/places")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "member" in data
        assert "totalItems" in data
        assert "limit" in data
        assert "offset" in data
        assert "next" in data

        assert data["totalItems"] == 3
        assert len(data["member"]) == 3
        assert data["limit"] == 50  # default limit
        assert data["offset"] == 0  # default offset

    def test_list_places_custom_pagination(self, client, sample_place_data):
        """Test listing places with custom limit and offset."""
        # Create 5 places
        for i in range(5):
            data = sample_place_data.copy()
            data["name"] = f"Place {i}"
            client.post("/places", json=data)

        # List with limit=2, offset=1
        response = client.get("/places?limit=2&offset=1")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["totalItems"] == 5
        assert len(data["member"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 1
        assert data["next"] is not None  # Should have next page

    def test_list_places_filter_by_status(self, client, sample_place_data):
        """Test filtering places by status."""
        # Create places with different statuses
        for status_value in ["open", "closed", "temporarily_closed"]:
            data = sample_place_data.copy()
            data["status"] = status_value
            data["name"] = f"Place {status_value}"
            client.post("/places", json=data)

        # Filter by status=open
        response = client.get("/places?status=open")
        data = response.json()

        assert data["totalItems"] == 1
        assert all(place["status"] == "open" for place in data["member"])

    def test_list_places_filter_by_type(self, client, sample_place_data):
        """Test filtering places by type."""
        # Create places with different types
        for place_type in ["shelter", "medical", "resource_center"]:
            data = sample_place_data.copy()
            data["type"] = place_type
            data["name"] = f"Place {place_type}"
            client.post("/places", json=data)

        # Filter by type=shelter
        response = client.get("/places?type=shelter")
        data = response.json()

        assert data["totalItems"] == 1
        assert all(place["type"] == "shelter" for place in data["member"])

    def test_list_places_filter_by_status_and_type(self, client, sample_place_data):
        """Test filtering places by both status and type."""
        # Create various combinations
        combinations = [
            ("shelter", "open"),
            ("shelter", "closed"),
            ("medical", "open"),
            ("medical", "closed"),
        ]

        for place_type, status_value in combinations:
            data = sample_place_data.copy()
            data["type"] = place_type
            data["status"] = status_value
            data["name"] = f"{place_type}_{status_value}"
            client.post("/places", json=data)

        # Filter by type=shelter AND status=open
        response = client.get("/places?type=shelter&status=open")
        data = response.json()

        assert data["totalItems"] == 1
        assert data["member"][0]["type"] == "shelter"
        assert data["member"][0]["status"] == "open"

    def test_list_places_next_link_generation(self, client, sample_place_data):
        """Test that 'next' link is correctly generated for pagination."""
        # Create 60 places (more than default limit of 50)
        for i in range(60):
            data = sample_place_data.copy()
            data["name"] = f"Place {i}"
            client.post("/places", json=data)

        # First page
        response = client.get("/places?limit=50&offset=0")
        data = response.json()

        assert data["next"] is not None
        assert "limit=50" in data["next"]
        assert "offset=50" in data["next"]

        # Last page
        response2 = client.get("/places?limit=50&offset=50")
        data2 = response2.json()

        assert data2["next"] is None  # No next page

    def test_list_places_ordered_by_updated_at_desc(self, client, sample_place_data):
        """Test that places are ordered by updated_at descending (most recent first)."""
        import time

        # Create places with small time delays
        place_ids = []
        for i in range(3):
            data = sample_place_data.copy()
            data["name"] = f"Place {i}"
            response = client.post("/places", json=data)
            place_ids.append(response.json()["id"])
            time.sleep(0.1)  # Small delay

        # List places
        response = client.get("/places")
        data = response.json()

        # Verify order (most recent first)
        returned_ids = [place["id"] for place in data["member"]]
        assert returned_ids == list(reversed(place_ids))


class TestPatchPlace:
    """Test suite for PATCH /places/{id} endpoint."""

    def test_patch_place_partial_update_success(self, client, sample_place_data, sample_place_minimal_data):
        """Test partially updating a place successfully."""
        # Create place
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Update only name and status
        update_data = {
            "name": "Updated Place Name",
            "status": "closed"
        }

        # Note: PATCH requires API key (we need to handle this in implementation)
        response = client.patch(
            f"/places/{place_id}",
            json=update_data,
            headers={"X-Api-Key": "test-api-key"}  # Mock API key for testing
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "Updated Place Name"
        assert data["status"] == "closed"
        # Other fields should remain unchanged
        assert data["address"] == sample_place_data["address"]
        assert data["contact_name"] == sample_place_data["contact_name"]

    def test_patch_place_update_jsonb_fields(self, client, sample_place_data):
        """Test updating JSONB fields (coordinates, resources, tags, additional_info)."""
        # Create place
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Update JSONB fields
        update_data = {
            "coordinates": {
                "lat": 24.0,
                "lng": 122.0
            },
            "resources": [
                {"type": "food", "quantity": 200}
            ],
            "tags": [
                {"name": "updated", "color": "blue"}
            ],
            "additional_info": {
                "updated": True
            }
        }

        response = client.patch(
            f"/places/{place_id}",
            json=update_data,
            headers={"X-Api-Key": "test-api-key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["coordinates"] == update_data["coordinates"]
        assert data["resources"] == update_data["resources"]
        assert data["tags"] == update_data["tags"]
        assert data["additional_info"] == update_data["additional_info"]

    def test_patch_place_not_found(self, client):
        """Test updating a non-existent place returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Updated"}

        response = client.patch(
            f"/places/{fake_id}",
            json=update_data,
            headers={"X-Api-Key": "test-api-key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_place_without_api_key_forbidden(self, client, sample_place_data):
        """Test that PATCH requires API key authentication."""
        # Create place
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Try to update without API key
        update_data = {"name": "Updated"}
        response = client.patch(f"/places/{place_id}", json=update_data)

        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_patch_place_empty_body_returns_400(self, client, sample_place_data):
        """Test that PATCH with no fields returns 400 (similar to Golang implementation)."""
        # Create place
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Try to update with empty body
        response = client.patch(
            f"/places/{place_id}",
            json={},
            headers={"X-Api-Key": "test-api-key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPlaceEdgeCases:
    """Test edge cases and special scenarios."""

    def test_create_place_with_empty_arrays(self, client, sample_place_minimal_data):
        """Test creating place with empty info_sources array."""
        data = sample_place_minimal_data.copy()
        data["info_sources"] = []

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_201_CREATED

        result = response.json()
        assert result["info_sources"] == []

    def test_create_place_with_null_optional_fields(self, client, sample_place_minimal_data):
        """Test creating place with explicitly null optional fields."""
        data = sample_place_minimal_data.copy()
        data["address_description"] = None
        data["sub_type"] = None
        data["website_url"] = None

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_places_empty_database(self, client):
        """Test listing places when database is empty."""
        response = client.get("/places")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["totalItems"] == 0
        assert data["member"] == []
        assert data["next"] is None

    def test_place_timestamps_auto_generated(self, client, sample_place_minimal_data):
        """Test that created_at and updated_at are automatically generated."""
        response = client.post("/places", json=sample_place_minimal_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] > 0  # Unix timestamp
        assert data["updated_at"] > 0
        assert data["created_at"] == data["updated_at"]  # Initially same


class TestCoordinatesValidation:
    """Test suite for coordinates field validation - Critical security tests."""

    def test_create_place_coordinates_missing_lat(self, client, sample_place_minimal_data):
        """Test that coordinates must have 'lat' field."""
        data = sample_place_minimal_data.copy()
        data["coordinates"] = {"lng": 121.1234}  # Missing 'lat'

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "lat" in str(error_detail).lower() or "coordinates" in str(error_detail).lower()

    def test_create_place_coordinates_missing_lng(self, client, sample_place_minimal_data):
        """Test that coordinates must have 'lng' field."""
        data = sample_place_minimal_data.copy()
        data["coordinates"] = {"lat": 23.5678}  # Missing 'lng'

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "lng" in str(error_detail).lower() or "coordinates" in str(error_detail).lower()

    def test_create_place_coordinates_wrong_type_array(self, client, sample_place_minimal_data):
        """Test that coordinates must be an object, not array."""
        data = sample_place_minimal_data.copy()
        data["coordinates"] = [23.5678, 121.1234]  # Array instead of object

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_coordinates_wrong_type_string(self, client, sample_place_minimal_data):
        """Test that coordinates must be an object, not string."""
        data = sample_place_minimal_data.copy()
        data["coordinates"] = "23.5678,121.1234"  # String instead of object

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEnumValidation:
    """Test suite for enum field validation - Critical security tests."""

    def test_create_place_invalid_type_enum(self, client, sample_place_minimal_data):
        """Test that invalid place type is rejected."""
        data = sample_place_minimal_data.copy()
        data["type"] = "invalid_type_not_in_enum"

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "type" in str(error_detail).lower()

    def test_create_place_invalid_status_enum(self, client, sample_place_minimal_data):
        """Test that invalid status is rejected."""
        data = sample_place_minimal_data.copy()
        data["status"] = "invalid_status_not_in_enum"

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "status" in str(error_detail).lower()

    def test_list_places_invalid_filter_type(self, client):
        """Test that invalid filter type returns 422."""
        response = client.get("/places?type=nonexistent_type")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_places_invalid_filter_status(self, client):
        """Test that invalid filter status returns 422."""
        response = client.get("/places?status=nonexistent_status")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("place_type", [
        "shelter", "medical", "resource_center", "supply_point",
        "information_center", "emergency_service", "volunteer_center",
        "temporary_housing", "other"
    ])
    def test_create_place_all_valid_types(self, client, sample_place_minimal_data, place_type):
        """Test all valid PlaceTypeEnum values are accepted."""
        data = sample_place_minimal_data.copy()
        data["type"] = place_type
        data["name"] = f"Test {place_type}"

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["type"] == place_type

    @pytest.mark.parametrize("status_value", [
        "open", "closed", "temporarily_closed", "full",
        "limited_capacity", "emergency_only"
    ])
    def test_create_place_all_valid_statuses(self, client, sample_place_minimal_data, status_value):
        """Test all valid PlaceStatusEnum values are accepted."""
        data = sample_place_minimal_data.copy()
        data["status"] = status_value
        data["name"] = f"Test {status_value}"

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == status_value


class TestJSONBStructureValidation:
    """Test suite for JSONB field structure validation - Critical security tests."""

    def test_create_place_resources_wrong_type_not_array(self, client, sample_place_minimal_data):
        """Test that resources must be array, not object or string."""
        data = sample_place_minimal_data.copy()
        data["resources"] = "not_an_array"  # String instead of array

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_tags_wrong_type_not_array(self, client, sample_place_minimal_data):
        """Test that tags must be array, not object."""
        data = sample_place_minimal_data.copy()
        data["tags"] = {"invalid": "structure"}  # Object instead of array

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_place_info_sources_wrong_type(self, client, sample_place_minimal_data):
        """Test that info_sources must be array of strings."""
        data = sample_place_minimal_data.copy()
        data["info_sources"] = "not_an_array"  # String instead of array

        response = client.post("/places", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_patch_place_jsonb_partial_update_preserves_other_fields(self, client, sample_place_data):
        """Test that updating one JSONB field doesn't affect other JSONB fields."""
        # Create place with all JSONB fields
        create_response = client.post("/places", json=sample_place_data)
        place_id = create_response.json()["id"]

        # Update only resources
        update_data = {
            "resources": [{"type": "updated_resource", "quantity": 999}]
        }

        response = client.patch(
            f"/places/{place_id}",
            json=update_data,
            headers={"X-Api-Key": "test-api-key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Resources should be updated
        assert data["resources"] == update_data["resources"]

        # Other JSONB fields should remain unchanged
        assert data["tags"] == sample_place_data["tags"]
        assert data["additional_info"] == sample_place_data["additional_info"]
        assert data["coordinates"] == sample_place_data["coordinates"]
