import json
import tempfile
from pathlib import Path

from msl.models import ProjectType
from msl.scanner import scan_project


def _tmp():
    return tempfile.TemporaryDirectory()


def test_scan_flutter_project():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "pubspec.yaml").write_text("name: my_app\nflutter:\n  sdk: flutter\n")
        (root / "test").mkdir()

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.FLUTTER
        assert scan.confidence >= 0.9
        assert "Flutter" in scan.frameworks
        assert "Dart" in scan.languages
        assert scan.name == "my_app"
        assert scan.has_tests is True


def test_scan_nextjs_project():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({
            "name": "my-next-app",
            "dependencies": {"next": "14.0.0", "react": "18.0.0"},
            "devDependencies": {"typescript": "5.0.0"},
        }))
        (root / "app").mkdir()
        (root / "tsconfig.json").write_text("{}")

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.NEXTJS
        assert "Next.js" in scan.frameworks
        assert "App Router" in scan.frameworks
        assert "TypeScript" in scan.languages
        assert scan.package_manager == "npm"


def test_scan_react_vite_project():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({
            "name": "my-react-app",
            "dependencies": {"react": "18.0.0", "vite": "5.0.0"},
        }))

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.REACT_VITE
        assert "React" in scan.frameworks
        assert "Vite" in scan.frameworks


def test_scan_nodejs_server_express():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({
            "name": "my-api",
            "dependencies": {"express": "4.18.0"},
        }))

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.NODEJS_SERVER
        assert "Express" in scan.frameworks


def test_scan_rust_axum_project():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "Cargo.toml").write_text('[package]\nname = "my-server"\n\n[dependencies]\naxum = "0.7"\ntokio = "1"\nsqlx = "0.7"\n')

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.RUST_SERVER
        assert "Rust" in scan.languages
        assert "Axum" in scan.frameworks
        assert scan.name == "my-server"


def test_scan_python_fastapi():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "pyproject.toml").write_text('[project]\nname = "myapi"\ndependencies = ["fastapi", "uvicorn"]\n')
        (root / "tests").mkdir()

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.PYTHON
        assert "Python" in scan.languages
        assert "Fastapi" in scan.frameworks
        assert scan.has_tests is True


def test_scan_go_gin_project():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text("module github.com/murad/myserver\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.0\n)\n")

        scan = scan_project(root)
        assert scan.detected_type == ProjectType.GO_SERVER
        assert "Go" in scan.languages
        assert "Gin" in scan.frameworks
        assert scan.name == "github.com/murad/myserver"


def test_scan_detects_pnpm():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({"name": "test"}))
        (root / "pnpm-lock.yaml").write_text("")

        scan = scan_project(root)
        assert scan.package_manager == "pnpm"


def test_scan_detects_ci():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / ".github" / "workflows").mkdir(parents=True)

        scan = scan_project(root)
        assert scan.has_ci is True


def test_scan_detects_docker():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "Dockerfile").write_text("FROM python:3.12")

        scan = scan_project(root)
        assert scan.has_docker is True


def test_scan_detects_monorepo():
    with _tmp() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(json.dumps({
            "name": "mono",
            "workspaces": ["packages/*"],
        }))

        scan = scan_project(root)
        assert scan.has_monorepo is True


def test_scan_empty_directory():
    with _tmp() as tmp:
        scan = scan_project(Path(tmp))
        assert scan.detected_type is None
        assert scan.confidence == 0.0
        assert scan.frameworks == []
