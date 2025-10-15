# Infinito Inventory Builder

## Description

**Infinito Inventory Builder** is a containerized web application that enables you to **interactively create Ansible inventory files** based on invokable roles from your **Infinito.Nexus** repository.

It provides a browser-based UI to select roles, define hosts, and export inventories in YAML format — perfectly aligned with the Infinito.Nexus role structure.

---

## Features

- ✅ **Automatic role discovery** using `roles/categories.yml` and `roles/list.json`
- 🧩 **Interactive selection** of invokable roles
- ⚙️ **Inventory generation styles:** `group` or `hostvars`
- 🗂️ **Downloadable YAML output**
- 🐳 **Containerized deployment** (FastAPI + React)
- 🔒 **Read-only mount** of your Infinito.Nexus repository

---

## Usage

```bash
docker compose up --build
````

Then open [http://localhost:5173](http://localhost:5173).

---

## API Endpoints

| Method | Endpoint              | Description                |
| ------ | --------------------- | -------------------------- |
| `GET`  | `/roles`              | Lists all invokable roles  |
| `GET`  | `/categories`         | Returns full category tree |
| `POST` | `/generate/inventory` | Builds an inventory file   |

---

## Environment Variables

| Variable                   | Default                | Description                        |
| -------------------------- | ---------------------- | ---------------------------------- |
| `WORKSPACE`                | `/workspace`           | Mount path for Infinito.Nexus repo |
| `RELATIVE_ROLES_DIR`       | `roles`                | Relative roles directory           |
| `RELATIVE_CATEGORIES_FILE` | `roles/categories.yml` | Category configuration file        |

---

## Example Output

### group-style

```yaml
all:
  hosts: [alpha]
  children:
    web-app-nextcloud: {}
web-app-nextcloud:
  hosts: [alpha]
```

### hostvars-style

```yaml
all:
  hosts: [alpha]
_meta:
  hostvars:
    alpha:
      invokable_applications:
        - web-app-nextcloud
```

---

## License

© Kevin Veen-Birkenbach
Licensed under the **Infinito.Nexus NonCommercial License**
[https://s.infinito.nexus/license](https://s.infinito.nexus/license)