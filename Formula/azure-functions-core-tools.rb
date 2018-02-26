 class AzureFunctionsCoreTools < Formula
  desc "Azure Function Cli 2.0"
  homepage "https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#run-azure-functions-core-tools"
  url "https://ci.appveyor.com/api/buildjobs/4i2wiosxpehv6wqm/artifacts/deploy%2FAzure.Functions.Cli.osx-x64.zip"
  sha256 "d99f03b54c399479246d6c395dd1fa93092769796e7a5bbd5c6b5da1c07fd766"
  head "https://github.com/Azure/azure-functions-core-tools"
  version "2.0.1-beta.22"
 
   def install
    prefix.install Dir["*"]
    chmod 0555, prefix/'func'
    bin.install_symlink prefix/'func'
  end
   test do
    # `test do` will create, run in and delete a temporary directory.
    #
    # This test will fail and we won't accept that! For Homebrew/homebrew-core
    # this will need to be a test that verifies the functionality of the
    # software. Run the test with `brew test azure-functions-core-tools`. Options passed
    # to `brew install` such as `--HEAD` also need to be provided to `brew test`.
    #
    # The installed folder is not in the path, so use the entire path to any
    # executables being tested: `system "#{bin}/program", "do", "something"`.
    system "false"
  end
end
