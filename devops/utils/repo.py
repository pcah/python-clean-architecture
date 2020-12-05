def get_repo():
    import git

    from devops import PROJECT_PACKAGE

    assert hasattr(PROJECT_PACKAGE, "PROJECT_DIR"), "No PROJECT_DIR variable declared"
    assert PROJECT_PACKAGE.PROJECT_DIR, "No PROJECT_DIR variable injected"
    return git.Repo(PROJECT_PACKAGE.PROJECT_DIR)
