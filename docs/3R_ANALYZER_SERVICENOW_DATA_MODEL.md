# ServiceNow Data Model

The platform is designed to ingest standard ServiceNow Incident exports.

## Supported Fields
| ServiceNow Field | Internal Model Name | Type | Nullable | Used in 3R/Clustering |
| :--- | :--- | :--- | :--- | :--- |
| Number | `incident_number` | String | No | No |
| Caller | `caller` | String | Yes | No |
| Short description | `short_description` | Text | Yes | **Yes** |
| Description | `description` | Text | Yes | **Yes** |
| Category | `category` | String | Yes | No |
| Subcategory | `subcategory` | String | Yes | No |
| Priority | `priority` | String | Yes | **Yes** |
| State | `state` | String | Yes | No |
| Assignment group | `assignment_group` | String | Yes | Yes (Metadata) |
| Assigned to | `assigned_to` | String | Yes | No |
| Resolved by | `resolved_by` | String | Yes | No |
| Configuration item | `configuration_item` | String | Yes | Yes (Metadata) |
| Offending CI | `offending_ci` | String | Yes | No |
| Offending CI Category | `offending_ci_category` | String | Yes | No |
| Business service | `business_service` | String | Yes | No |
| Region | `region` | String | Yes | No |
| KB Number | `kb_number` | String | Yes | No |
| IT Batch Job | `it_batch_job` | String | Yes | No |
| Reassignment count | `reassignment_count` | Integer | Yes | No |
| Created | `created_date` | DateTime | Yes | **Yes (Time Series)** |
| Resolved | `resolved_date` | DateTime | Yes | No |

## Dynamic Workspace
All the above fields are fully exposed in the Incident Investigation Workspace, allowing users to dynamically select them as columns and filter by them.
